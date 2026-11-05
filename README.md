<p align="center">
  <h1 align="center">🧬 TrueAgent</h1>
  <p align="center"><strong>Universal AI Agent Enhancement Framework</strong></p>
  <p align="center">Cross-platform autonomy, dual-engine browser automation, neural voice feedback, and pre-push safety across Claude Code, Cursor, Codex, Windsurf, and Antigravity.</p>
</p>

<p align="center">
  <a href="https://github.com/ATP0925/trueagent/actions"><img src="https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"></a>
  <a href="https://github.com/ATP0925/trueagent"><img src="https://img.shields.io/badge/python-3.8+-informational?style=flat-square" alt="Python Version"></a>
  <a href="https://github.com/ATP0925/trueagent"><img src="https://img.shields.io/badge/platforms-7-success?style=flat-square" alt="Platforms"></a>
</p>

---

## 🌟 Overview

**TrueAgent** bridges the gap between text-generating coding models and true execution autonomy. It equips any assistant with:
1. **🌐 WebPilot:** Dual-engine browser automation over CDP with automatic failover and RFC 6238 2FA token generation.
2. **🎙️ VoxCore:** 3-tier zero-fail neural speech synthesis (Edge-TTS -> gTTS -> OS Native) with configurable callsign.
3. **🛡️ SentinelGuard:** Integrated PII scanner and pre-push secret shield.
4. **🔍 ReviewForge:** Clean-room git diff analysis and code quality scanner.
5. **⚡ CortexRouter:** Hardware-aware compute director that routes tasks based on available system RAM.

---

## 🚀 Quickstart

### 1. Configuration
Customize `trueagent.config.json`:
```json
{
  "version": "1.0.0",
  "persona": {
    "callsign": "Operator",
    "tone": "concise",
    "voice_feedback": true
  },
  "browser": {
    "primary_browser": "brave",
    "primary_port": 9222,
    "secondary_browser": "chrome",
    "secondary_port": 9223
  },
  "hardware": {
    "ram_cloud_threshold_gb": 4.0
  }
}
```

### 2. Run WebPilot
```bash
python -m core.webpilot.pilot status
python -m core.webpilot.pilot open github
```

### 3. Run ReviewForge
```bash
python -c "from core.reviewforge.reviewer import ReviewForge; print(ReviewForge.format_report_markdown(ReviewForge.analyze_diff(ReviewForge.get_git_diff())))"
```

---

## 🛠️ Supported Platforms

* **Claude Code:** Configured via `platforms/claude/CLAUDE.md`.
* **Cursor:** Configured via `platforms/cursor/rules/trueagent.mdc`.
* **OpenAI Codex:** Configured via `platforms/codex/AGENTS.md`.
* **Google Antigravity:** Integrated via `platforms/antigravity/plugin.json`.
* **Canonical Standard:** Defined in root `AGENTS.md`.

---

## 🧪 Testing

```bash
python -m unittest discover -s tests
```

---

## 🤝 License

Licensed under the [MIT License](LICENSE). 100% original, clean-room implementation.
