# 🧬 TrueAgent Universal Rules

These instructions apply to all AI assistants operating in this workspace.

## 🛡️ Security Protocol
- Never commit or stage `.env*`, `.pem`, `.key`, or credentials.
- Do not execute destructive recursive deletion commands (`rm -rf /` or `rmdir /s /q`).
- Ensure all git pushes pass the SentinelGuard pre-push scanner.

## 🌐 Browser Automation Protocol
- Web automation is handled via WebPilot on remote debugging ports configured in `trueagent.config.json` (defaults: Primary 9222, Secondary 9223).
- Always prefer semantic ARIA selectors (`[role="button"][aria-label*="..."]`) over brittle absolute XPath selectors.

## 🎙️ Feedback Protocol
- Voice feedback uses VoxCore with 3-tier synthesis.
- Verbal messages must be concise, bottom-line focused, and address the configured callsign.

## 🔍 Code Quality Protocol
- Before finalizing code changes, execute ReviewForge quality checks.
- Eliminate residual debug logs (`console.log`, `debugger`, `print()`) before committing.
