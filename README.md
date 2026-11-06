<p align="center">
  <h1 align="center">🧬 TrueAgent</h1>
  <p align="center"><strong>Universal AI Agent Enhancement Framework</strong></p>
  <p align="center">Cross-platform autonomy, dual-engine browser automation, neural voice feedback, and pre-push safety across Claude Code, Cursor, Codex, Windsurf, and Google Antigravity.</p>
</p>

<p align="center">
  <a href="https://github.com/ATP0925/trueagent/actions"><img src="https://img.shields.io/badge/tests-22%20passing-brightgreen?style=flat-square" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"></a>
  <a href="https://github.com/ATP0925/trueagent"><img src="https://img.shields.io/badge/python-3.8+-informational?style=flat-square" alt="Python Version"></a>
  <a href="https://github.com/ATP0925/trueagent"><img src="https://img.shields.io/badge/platforms-7-success?style=flat-square" alt="Platforms"></a>
</p>

---

## 🌟 Overview

**TrueAgent** bridges the gap between text-generating coding models and true execution autonomy. It equips any coding assistant with:
1. **🌐 WebPilot:** Dual-engine browser automation over CDP with automatic failover (Brave 9222 -> Chrome 9223) and RFC 6238 2FA token generation.
2. **🎙️ VoxCore:** 3-tier zero-fail neural speech synthesis (Edge-TTS -> gTTS -> OS Native) with configurable user callsign.
3. **🛡️ SentinelGuard:** Integrated PII scanner and pre-push secret shield.
4. **🔍 ReviewForge:** Clean-room git diff analysis and code quality scanner.
5. **⚡ CortexRouter:** Hardware-aware compute director that routes tasks based on available system RAM.

---

## 🚀 Quick Setup (1-Command Automatic Wizard)

Clone the repository and run the setup wizard in your target project:

```bash
git clone https://github.com/ATP0925/trueagent.git
cd trueagent
```

### Auto-Configure for All Installed AI Assistants:
```bash
python setup_trueagent.py --platform all --target /path/to/your/project
```

### Or Configure for a Specific Platform:
```bash
# For Google Antigravity IDE
python setup_trueagent.py --platform antigravity --target /path/to/your/project

# For Claude Code
python setup_trueagent.py --platform claude --target /path/to/your/project

# For Cursor IDE
python setup_trueagent.py --platform cursor --target /path/to/your/project

# For OpenAI Codex / Copilot
python setup_trueagent.py --platform codex --target /path/to/your/project
```

---

## 📖 Manual Step-by-Step Setup by Platform

If you prefer configuring manually without running the wizard script:

### 1. 🟣 Google Antigravity IDE
TrueAgent integrates natively as an Antigravity plugin and builtin workspace rules:
1. Copy the plugin manifest:
   ```bash
   mkdir -p ~/.gemini/config/plugins/trueagent
   cp platforms/antigravity/plugin.json ~/.gemini/config/plugins/trueagent/plugin.json
   ```
2. Copy `AGENTS.md` and `trueagent.config.json` into your workspace root.
3. Antigravity IDE will automatically detect the plugin and enforce the rules on agent launch.

### 2. 🟠 Claude Code (Terminal)
Claude Code looks for `CLAUDE.md` in the project root:
1. Copy `platforms/claude/CLAUDE.md` to your repository root as `CLAUDE.md`.
2. Copy `AGENTS.md` and `trueagent.config.json` to your repository root.
3. When running `claude`, Claude Code imports the rules automatically.

### 3. 🔵 Cursor IDE
Cursor uses `.cursor/rules/*.mdc` for context-aware instructions:
1. Create the rules folder:
   ```bash
   mkdir -p .cursor/rules
   ```
2. Copy `platforms/cursor/rules/trueagent.mdc` into `.cursor/rules/trueagent.mdc`.
3. Copy `AGENTS.md` into your project root.
4. Cursor Composer and Chat will automatically load the rules with `alwaysApply: true`.

### 4. 🟢 OpenAI Codex & GitHub Copilot
Codex and Copilot natively read repository-level markdown instructions:
1. Copy `AGENTS.md` into your repository root.
2. If using GitHub Copilot Workspace, also copy or symlink `AGENTS.md` to `.github/copilot-instructions.md`.

### 5. 🌊 Windsurf (Codeium), Cline & Aider
- **Windsurf:** Copy `AGENTS.md` as `.windsurfrules` in the project root.
- **Cline / Roo Code:** Copy `AGENTS.md` as `.clinerules` in the project root.
- **Aider:** Copy `AGENTS.md` as `CONVENTIONS.md`.

---

## 🌐 Launching the Authorized AI Browser (CDP Remote Debugging)

To enable **WebPilot** browser automation, launch your browser with remote debugging enabled:

### Windows (PowerShell):
```powershell
# For Brave Browser (Primary - Port 9222)
& "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222 --user-data-dir="$HOME\.authorized_ai_browser" --remote-allow-origins=*

# For Google Chrome (Secondary Failover - Port 9223)
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="$HOME\.authorized_ai_browser" --remote-allow-origins=*
```

### macOS:
```bash
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser --remote-debugging-port=9222 --user-data-dir="$HOME/.authorized_ai_browser" --remote-allow-origins=* &
```

### Linux:
```bash
brave-browser --remote-debugging-port=9222 --user-data-dir="$HOME/.authorized_ai_browser" --remote-allow-origins=* &
```

---

## ⚙️ Configuration (`trueagent.config.json`)

All modules read dynamically from `trueagent.config.json` in your project root:

```json
{
  "version": "1.0.0",
  "persona": {
    "callsign": "Operator",
    "tone": "concise",
    "voice_feedback": true,
    "language": "hi-IN"
  },
  "browser": {
    "primary_browser": "brave",
    "primary_port": 9222,
    "secondary_browser": "chrome",
    "secondary_port": 9223,
    "headless": false,
    "handoff_timeout_seconds": 60
  },
  "hardware": {
    "ram_cloud_threshold_gb": 4.0,
    "monitor_resources": true
  },
  "presets": {
    "github": "https://github.com",
    "docs": "https://devdocs.io",
    "stackoverflow": "https://stackoverflow.com",
    "youtube": "https://www.youtube.com",
    "local_app": "http://localhost:3000"
  },
  "security": {
    "enable_sentinel": true,
    "pre_push_confirmation_steps": 2
  }
}
```

* **`persona.callsign`**: Name or title the voice engine addresses you by (e.g. "Developer", "Boss", "Alex").
* **`browser.primary_port` / `secondary_port`**: Debugging ports for primary and failover browser engines.
* **`hardware.ram_cloud_threshold_gb`**: Memory floor below which heavy tasks are routed to cloud APIs.

---

## 🧪 Testing

Verify that all modules and configurations pass tests:
```bash
python -m unittest discover -s tests
```

---

## 🤝 License

Licensed under the [MIT License](LICENSE). 100% clean-room, original implementation.
