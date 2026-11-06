"""
VoxCore: Neural Voice Synthesis Engine for TrueAgent.
Provides resilient, 3-tier speech synthesis with configurable user callsign.
"""

import sys
import os
import re
import subprocess
import asyncio
import json
import uuid
import tempfile
from typing import Optional


ACRONYM_MAP = {
    r"\bAPI\b": "A-P-I",
    r"\bAPIs\b": "A-P-Is",
    r"\bCDP\b": "C-D-P",
    r"\bPR\b": "P-R",
    r"\bPRs\b": "P-Rs",
    r"\bCLI\b": "C-L-I",
    r"\bSDK\b": "S-D-K",
    r"\bURL\b": "U-R-L",
    r"\bURLs\b": "U-R-Ls",
    r"\bTTS\b": "T-T-S",
    r"\bDB\b": "Database",
    r"\bE2E\b": "End to End",
    r"\bUI\b": "U-I",
    r"\bUX\b": "U-X",
    r"\bJWT\b": "J-W-T",
    r"\bOAuth\b": "O-Auth"
}


def load_config() -> dict:
    candidates = [
        os.path.join(os.getcwd(), "trueagent.config.json"),
        os.path.expanduser("~/.trueagent.json")
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                with open(c, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {"persona": {"callsign": "Operator", "language": "hi-IN"}}


def sanitize_text(text: str, callsign: str = "Operator") -> str:
    """Strips markdown code blocks, links, paths, and prepends callsign."""
    # Remove code blocks
    clean = re.sub(r"```[\s\S]*?```", "", text)
    clean = re.sub(r"`[^`]*`", "", clean)
    # Remove markdown links [Text](url) -> Text
    clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
    # Remove URLs
    clean = re.sub(r"https?://\S+", "", clean)
    # Remove local filesystem paths
    clean = re.sub(r"[A-Za-z]:\\[\w\\]+", "", clean)
    clean = re.sub(r"/[a-zA-Z0-9_\-./]+", "", clean)
    # Remove markdown formatting characters
    clean = re.sub(r"[*_~#>`|]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    # Expand technical acronyms
    for pattern, replacement in ACRONYM_MAP.items():
        clean = re.sub(pattern, replacement, clean)

    if callsign and not clean.lower().startswith(callsign.lower()):
        clean = f"{callsign}, {clean}"

    return clean


async def speak_edge_tts(text: str, voice: str = "hi-IN-MadhurNeural") -> bool:
    """Tier 1: Cloud neural speech via edge-tts."""
    try:
        import edge_tts
        temp_mp3 = os.path.join(tempfile.gettempdir(), f"trueagent_vox_{uuid.uuid4().hex[:8]}.mp3")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(temp_mp3)
        play_audio(temp_mp3)
        return True
    except Exception:
        return False


def speak_gtts(text: str, lang: str = "hi") -> bool:
    """Tier 2: Cloud fallback speech via gTTS."""
    try:
        from gtts import gTTS
        temp_mp3 = os.path.join(tempfile.gettempdir(), f"trueagent_vox_{uuid.uuid4().hex[:8]}.mp3")
        tts = gTTS(text=text, lang=lang)
        tts.save(temp_mp3)
        play_audio(temp_mp3)
        return True
    except Exception:
        return False


def speak_native(text: str) -> bool:
    """Tier 3: 100% offline OS native speech."""
    try:
        if sys.platform == "win32":
            # Pass text via stdin to prevent PowerShell injection
            ps_script = '''
            Add-Type -AssemblyName System.Speech
            $text = [Console]::In.ReadToEnd()
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.Speak($text)
            '''
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                input=text, text=True, check=True, timeout=15,
                capture_output=True
            )
            return True
        elif sys.platform == "darwin":
            subprocess.run(["say", text], check=True, timeout=10)
            return True
        else:
            subprocess.run(["espeak", text], check=True, timeout=10)
            return True
    except Exception:
        return False


def play_audio(file_path: str):
    """Plays audio via available OS media handlers."""
    if sys.platform == "win32":
        # Route 1: ffplay
        try:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path], check=True, timeout=15)
            return
        except Exception:
            pass
        # Route 2: WMPlayer COM (plays MP3 natively)
        try:
            ps_cmd = (
                f'$p = New-Object -ComObject WMPlayer.OCX;'
                f'$p.URL = "{file_path.replace(chr(92), "/")}";'
                f'$p.controls.play();'
                f'Start-Sleep -Milliseconds 500;'
                f'while($p.playState -eq 3){{Start-Sleep -Milliseconds 100}};'
                f'$p.close();'
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=20, capture_output=True)
            return
        except Exception:
            pass
        # Route 3: PowerShell SoundPlayer (WAV only)
        try:
            ps_cmd = f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=15)
        except Exception:
            pass


def _run_async_tts(text: str, voice: str = "hi-IN-MadhurNeural") -> bool:
    """Runs async TTS in dedicated event loop thread."""
    import threading
    result = [False]
    def _worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result[0] = loop.run_until_complete(speak_edge_tts(text, voice))
        finally:
            loop.close()
    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout=20)
    return result[0]


def speak(text: str, custom_callsign: str = None):
    """Unified entrypoint: Executes 3-tier zero-fail speech synthesis."""
    cfg = load_config()
    callsign = custom_callsign or cfg.get("persona", {}).get("callsign", "Operator")
    clean = sanitize_text(text, callsign)

    # Tier 1 - use dedicated event loop to avoid nested asyncio.run() crash
    try:
        success = _run_async_tts(clean)
        if success:
            return
    except Exception:
        pass

    # Tier 2
    if speak_gtts(clean):
        return

    # Tier 3 (Offline guaranteed)
    speak_native(clean)


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "TrueAgent voice engine initialized."
    speak(msg)

