"""
TrueAgent Setup & Configuration Wizard:
Auto-detects your workspace and installs TrueAgent rules into your AI coding tool
(Claude Code, Cursor, Codex, Windsurf, or Google Antigravity).
"""

import os
import sys
import shutil
import argparse
import json


def safe_copy(src: str, dst: str):
    """Copies file only if source and destination are different paths."""
    if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
        os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
        shutil.copy2(src, dst)


def setup_antigravity(repo_root: str, target_dir: str):
    print("  📦 Installing TrueAgent into Google Antigravity IDE...")
    home = os.path.expanduser("~")
    ide_plugin_dir = os.path.join(home, ".gemini", "config", "plugins", "trueagent")
    os.makedirs(ide_plugin_dir, exist_ok=True)
    
    src_plugin = os.path.join(repo_root, "platforms", "antigravity", "plugin.json")
    safe_copy(src_plugin, os.path.join(ide_plugin_dir, "plugin.json"))
        
    safe_copy(os.path.join(repo_root, "AGENTS.md"), os.path.join(target_dir, "AGENTS.md"))
    print(f"  ✓ Antigravity plugin registered at: {ide_plugin_dir}")
    print(f"  ✓ Workspace AGENTS.md verified at: {target_dir}")


def setup_claude(repo_root: str, target_dir: str):
    print("  📦 Installing TrueAgent for Claude Code...")
    claude_target = os.path.join(target_dir, "CLAUDE.md")
    src_claude = os.path.join(repo_root, "platforms", "claude", "CLAUDE.md")
    safe_copy(src_claude, claude_target)
    safe_copy(os.path.join(repo_root, "AGENTS.md"), os.path.join(target_dir, "AGENTS.md"))
    print(f"  ✓ Created CLAUDE.md and AGENTS.md in {target_dir}")


def setup_cursor(repo_root: str, target_dir: str):
    print("  📦 Installing TrueAgent for Cursor...")
    rules_dir = os.path.join(target_dir, ".cursor", "rules")
    os.makedirs(rules_dir, exist_ok=True)
    src_rule = os.path.join(repo_root, "platforms", "cursor", "rules", "trueagent.mdc")
    safe_copy(src_rule, os.path.join(rules_dir, "trueagent.mdc"))
    safe_copy(os.path.join(repo_root, "AGENTS.md"), os.path.join(target_dir, "AGENTS.md"))
    print(f"  ✓ Created .cursor/rules/trueagent.mdc in {target_dir}")


def setup_codex(repo_root: str, target_dir: str):
    print("  📦 Installing TrueAgent for OpenAI Codex / Copilot...")
    safe_copy(os.path.join(repo_root, "AGENTS.md"), os.path.join(target_dir, "AGENTS.md"))
    print(f"  ✓ Created AGENTS.md in {target_dir}")


def setup_browser_daemon(primary_port: int = 9222):
    print(f"  🌐 Remote Browser Debugging Setup (Port {primary_port}):")
    if sys.platform == "win32":
        brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        exe = brave_path if os.path.exists(brave_path) else chrome_path
        print("  Run this command in terminal to launch your AI-authorized browser:")
        print(f'  & "{exe}" --remote-debugging-port={primary_port} --user-data-dir="$env:USERPROFILE\\.authorized_ai_browser" --remote-allow-origins=*')
    else:
        print(f"  google-chrome --remote-debugging-port={primary_port} --user-data-dir=\"$HOME/.authorized_ai_browser\" &")


def main():
    parser = argparse.ArgumentParser(description="TrueAgent Multi-AI Setup Wizard")
    parser.add_argument("--platform", choices=["all", "antigravity", "claude", "cursor", "codex"], default="all", help="Target AI tool")
    parser.add_argument("--target", type=str, default=os.getcwd(), help="Target workspace directory")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.abspath(args.target)

    print("\n" + "=" * 60)
    print("🧬 TrueAgent Setup Wizard")
    print(f"Target Workspace: {target_dir}")
    print("=" * 60 + "\n")

    # Ensure config file exists
    cfg_dst = os.path.join(target_dir, "trueagent.config.json")
    if not os.path.exists(cfg_dst):
        safe_copy(os.path.join(repo_root, "trueagent.config.json"), cfg_dst)
        print("✓ Created trueagent.config.json in workspace.")

    if args.platform in ["all", "antigravity"]:
        setup_antigravity(repo_root, target_dir)
    if args.platform in ["all", "claude"]:
        setup_claude(repo_root, target_dir)
    if args.platform in ["all", "cursor"]:
        setup_cursor(repo_root, target_dir)
    if args.platform in ["all", "codex"]:
        setup_codex(repo_root, target_dir)

    print("\n" + "-" * 60)
    setup_browser_daemon()
    print("-" * 60)
    print("\n✅ TrueAgent setup completed successfully! Your workspace is enhanced.\n")


if __name__ == "__main__":
    main()
