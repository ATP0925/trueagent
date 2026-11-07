import unittest
import sys
import os

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

from core.cortex.router import CortexRouter, SystemMemoryInfo
from core.webpilot.totp import generate_totp, verify_totp
from core.reviewforge.reviewer import ReviewForge
from core.sentinel.guard import SentinelGuard
from core.voxcore.speak import sanitize_text, speak_native
from core.voxcore.duplex import VoxBargeInCoordinator, VoxAudioStreamManager
from unittest.mock import patch
import numpy as np


class TestTrueAgent(unittest.TestCase):

    def setUp(self):
        # Reset any shared state between tests
        pass

    def test_cortex_memory_retrieval(self):
        ram = SystemMemoryInfo.get_available_ram_gb()
        self.assertGreater(ram, 0.0)

    def test_cortex_router_defaults(self):
        router = CortexRouter()
        self.assertEqual(router.get_user_callsign(), "Operator")
        self.assertEqual(router.resolve_browser_port("primary"), 9222)
        self.assertEqual(router.resolve_browser_port("secondary"), 9223)

    def test_webpilot_totp_generation(self):
        # RFC 6238 test secret
        secret = "JBSWY3DPEHPK3PXP"
        token = generate_totp(secret)
        self.assertEqual(len(token), 6)
        self.assertTrue(token.isdigit())

    def test_reviewforge_diff_analysis(self):
        fake_diff = (
            "+++ b/app.py\n"
            "+console.log('debug message');\n"
            "+query = 'SELECT * FROM users WHERE id = ' + user_id;\n"
            "+try:\n"
            "+    do_something()\n"
            "+except:\n"
            "+    pass\n"
        )
        analysis = ReviewForge.analyze_diff(fake_diff)
        self.assertEqual(analysis["total_files"], 1)
        self.assertEqual(analysis["total_findings"], 3)
        for f in analysis["findings"]:
            self.assertIn("line", f)
            self.assertIn("rule", f)
            self.assertIsInstance(f["line"], int)
            self.assertIsInstance(f["rule"], str)

    def test_sentinel_guard_detects_secrets(self):
        guard = SentinelGuard()
        test_key = "AKIA" + "IOSFODNN7EXAMPLE"
        diff = f"+aws_key = '{test_key}'"
        findings = guard.scan_diff(diff)
        self.assertTrue(any(f["type"] == "aws_access_key" for f in findings))

    def test_sentinel_guard_scan_text_normal_file(self):
        guard = SentinelGuard()
        # Programmatically construct secret token to avoid hardcoding real-looking secrets
        test_token = "sk_live_" + "1234567890abcdefABCDEF12"
        file_content = f"DATABASE_URL = 'sqlite:///test.db'\nSTRIPE_KEY = '{test_token}'\nDEBUG = False\n"
        findings = guard.scan_text(file_content, source_name="settings.py")
        self.assertTrue(any(f["type"] == "stripe_api_key" for f in findings))
        self.assertEqual(findings[0]["source"], "settings.py")
        self.assertEqual(findings[0]["line"], 2)

    def test_sentinel_guard_scan_text_diff_autodetect(self):
        guard = SentinelGuard()
        test_key = "AKIA" + "1234567890ABCDEF"
        diff_text = f"diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n+aws_key = '{test_key}'\n"
        findings = guard.scan_text(diff_text)
        self.assertTrue(any(f["type"] == "aws_access_key" for f in findings))

    def test_voxcore_sanitization(self):
        raw = "```python\nprint('hello')\n``` Check out [link](https://example.com) for API docs."
        clean = sanitize_text(raw, callsign="Operator")
        self.assertTrue(clean.startswith("Operator,"))
        self.assertNotIn("https://", clean)
        self.assertIn("A-P-I", clean)

    def test_voxcore_barge_in_coordination(self):
        coord = VoxBargeInCoordinator()
        self.assertEqual(coord.state, "IDLE")
        coord.set_speaking()
        self.assertEqual(coord.state, "SPEAKING")
        self.assertEqual(coord.turns_count, 1)
        coord.trigger_interruption()
        self.assertEqual(coord.state, "INTERRUPTED")
        self.assertEqual(coord.interruption_count, 1)

        # Mute test
        coord.set_muted()
        self.assertEqual(coord.state, "MUTED")
        is_muted = coord.toggle_mute()
        self.assertFalse(is_muted)
        self.assertEqual(coord.state, "IDLE")

    def test_voxcore_dsp_highpass_filtering(self):
        mgr_fan = VoxAudioStreamManager(input_rate=16000)
        mgr_voice = VoxAudioStreamManager(input_rate=16000)
        t = np.linspace(0, 0.05, 800)
        fan_100 = np.sin(2 * np.pi * 100 * t)
        voice_500 = np.sin(2 * np.pi * 500 * t)

        filtered_fan = mgr_fan.filter_audio(fan_100)
        filtered_voice = mgr_voice.filter_audio(voice_500)

        rms_fan = np.sqrt(np.mean(filtered_fan**2))
        rms_voice = np.sqrt(np.mean(filtered_voice**2))

        # Fan noise attenuated, human voice preserved
        self.assertLess(rms_fan, 0.35)
        self.assertGreater(rms_voice, 0.50)

    def test_voxcore_output_callback_queue_buffering(self):
        mgr = VoxAudioStreamManager(input_rate=16000, output_rate=24000, chunk_size=256)
        # Put 1000 bytes into output queue (500 int16 samples)
        dummy_pcm = (np.ones(500, dtype=np.int16) * 1000).tobytes()
        mgr.output_queue.put(dummy_pcm)

        outdata = np.zeros((256, 1), dtype=np.float32)
        mgr._output_callback(outdata, frames=256, time_info=None, status=None)
        self.assertTrue(mgr.is_playing)
        # Verify remainder was put back in output_queue thread-safely
        self.assertFalse(mgr.output_queue.empty())
        rem_chunk = mgr.output_queue.get_nowait()
        self.assertEqual(len(rem_chunk), 1000 - (256 * 2))

    def test_voxcore_speak_native_stdin(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            success = speak_native("Hello test voice")
            self.assertTrue(success)
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            if sys.platform == "win32":
                self.assertIn("-NoProfile", args[0])
                self.assertEqual(kwargs.get("input"), "Hello test voice")

    def test_sentinel_guard_detects_sts_and_unquoted_secrets(self):
        guard = SentinelGuard()
        # Programmatic construction
        sts_token = "ASIA" + "1234567890ABCDEF"
        unquoted_secret = "api_key = " + "TestSecret123456Key!"
        diff_text = f"+sts = '{sts_token}'\n+{unquoted_secret}\n"
        findings = guard.scan_diff(diff_text)
        types = [f["type"] for f in findings]
        self.assertIn("aws_sts_key", types)
        self.assertIn("generic_secret_unquoted", types)
        for f in findings:
            self.assertIn("rule", f)
            self.assertIn("line", f)

    def test_voxcore_odd_byte_truncation_safety(self):
        mgr = VoxAudioStreamManager(input_rate=16000, output_rate=24000, chunk_size=256)
        # Put 257 bytes into output queue (odd bytes, partial buffer < needed 512)
        odd_bytes = b"\x01" * 257
        mgr.output_queue.put(odd_bytes)

        outdata = np.zeros((256, 1), dtype=np.float32)
        # Must not raise ValueError: buffer size must be a multiple of element size
        mgr._output_callback(outdata, frames=256, time_info=None, status=None)
        self.assertTrue(mgr.is_playing)

    def test_voxcore_speak_inside_event_loop(self):
        import asyncio
        from core.voxcore.speak import speak
        with patch("core.voxcore.speak._run_async_tts", return_value=True) as mock_tts:
            async def run_inside_loop():
                speak("Test voice from async loop")
            asyncio.run(run_inside_loop())
            mock_tts.assert_called_once()

    def test_voxcore_play_audio_wmplayer_com(self):
        from core.voxcore.speak import play_audio
        with patch("subprocess.run") as mock_run:
            # Route 1 (ffplay) fails, triggering Route 2 (WMPlayer COM)
            mock_run.side_effect = [Exception("ffplay not found"), unittest.mock.MagicMock(returncode=0)]
            play_audio("C:/temp/test.mp3")
            self.assertEqual(mock_run.call_count, 2)
            args, kwargs = mock_run.call_args_list[1]
            self.assertIn("WMPlayer.OCX", args[0][3])

    def test_webpilot_totp_verification(self):
        secret = "JBSWY3DPEHPK3PXP"
        current_code = generate_totp(secret)
        self.assertTrue(verify_totp(secret, current_code))
        prev_code = generate_totp(secret, time_offset=-1)
        self.assertTrue(verify_totp(secret, prev_code, window=1))
        next_code = generate_totp(secret, time_offset=1)
        self.assertTrue(verify_totp(secret, next_code, window=1))
        # Invalid code check
        self.assertFalse(verify_totp(secret, "000000" if current_code != "000000" else "111111"))

    def test_webpilot_totp_invalid_secret(self):
        with self.assertRaises(ValueError) as ctx:
            generate_totp("invalid! secret! with illegal base32 characters #@$")
        self.assertIn("Invalid TOTP secret", str(ctx.exception))

    def test_voxcore_sanitization_preserves_fractions(self):
        raw = "Our accuracy reached 95 / 100 on the evaluation benchmark."
        clean = sanitize_text(raw, callsign="Operator")
        self.assertIn("95 / 100", clean)

    def test_voxcore_sanitization_removes_filesystem_paths(self):
        raw = "Check the logs at /var/log/app/server.log and /usr/local/bin/python"
        clean = sanitize_text(raw, callsign="Operator")
        self.assertNotIn("/var/log/app/server.log", clean)
        self.assertNotIn("/usr/local/bin/python", clean)

    def test_trueagent_cli_subcommands_and_no_dead_import(self):
        from pathlib import Path
        import subprocess
        cli_path = Path(pkg_root) / "trueagent_cli.py"
        src = cli_path.read_text(encoding="utf-8")
        self.assertNotIn("sanitize_text", src)

        res = subprocess.run([sys.executable, str(cli_path), "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("speak", res.stdout)
        self.assertIn("browser", res.stdout)
        self.assertIn("duplex", res.stdout)

    def test_setup_powershell_userprofile(self):
        from pathlib import Path
        setup_path = Path(pkg_root) / "setup_trueagent.py"
        src = setup_path.read_text(encoding="utf-8")
        self.assertNotIn("%USERPROFILE%", src)
        self.assertIn("$env:USERPROFILE", src)

    def test_voxcore_speaking_lock_and_abort(self):
        from core.voxcore.speak import _set_speaking_lock, LOCK_FILE, ABORT_FILE
        import tempfile
        _set_speaking_lock(True)
        self.assertTrue(os.path.exists(LOCK_FILE))
        _set_speaking_lock(False)
        self.assertFalse(os.path.exists(LOCK_FILE))


if __name__ == "__main__":
    unittest.main()
