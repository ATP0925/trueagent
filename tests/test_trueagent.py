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
from core.voxcore.speak import sanitize_text
from core.voxcore.duplex import VoxBargeInCoordinator, VoxAudioStreamManager
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
        diff = "+aws_key = 'AKIAIOSFODNN7EXAMPLE'"
        findings = guard.scan_diff(diff)
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


if __name__ == "__main__":
    unittest.main()
