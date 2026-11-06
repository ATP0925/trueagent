import unittest
import sys
import os

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

from core.cortex.router import CortexRouter, SystemMemoryInfo
from core.webpilot.totp import generate_totp
from core.reviewforge.reviewer import ReviewForge
from core.sentinel.guard import SentinelGuard
from core.voxcore.speak import sanitize_text, speak_native
from core.voxcore.duplex import VoxBargeInCoordinator, VoxAudioStreamManager
from unittest.mock import patch
import numpy as np


class TestTrueAgent(unittest.TestCase):

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
        mgr = VoxAudioStreamManager(input_rate=16000)
        t = np.linspace(0, 0.05, 800)
        fan_100 = np.sin(2 * np.pi * 100 * t)
        voice_500 = np.sin(2 * np.pi * 500 * t)

        filtered_fan = mgr.filter_audio(fan_100)
        filtered_voice = mgr.filter_audio(voice_500)

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


if __name__ == "__main__":
    unittest.main()
