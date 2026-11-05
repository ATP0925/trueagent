"""
WebPilot CLI & Workflow Controller for TrueAgent.
Generic, configurable browser automation.
"""

import sys
import os
import json
import argparse
from .cdp_engine import CDPEngine
from .failover import FailoverNavigator
from .totp import generate_totp


DEFAULT_PRESETS = {
    "github": "https://github.com",
    "docs": "https://devdocs.io",
    "stackoverflow": "https://stackoverflow.com",
    "youtube": "https://www.youtube.com",
    "local_app": "http://localhost:3000"
}


def load_presets() -> dict:
    config_path = os.path.join(os.getcwd(), "trueagent.config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return cfg.get("presets", DEFAULT_PRESETS)
        except Exception:
            pass
    return DEFAULT_PRESETS


def main():
    parser = argparse.ArgumentParser(prog="webpilot", description="Browser automation engine for TrueAgent.")
    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Check status of browser engines")

    # open
    p_open = subparsers.add_parser("open", help="Open a URL or preset")
    p_open.add_argument("target", type=str, help="URL or preset name (github, docs, stackoverflow...)")

    # totp
    p_totp = subparsers.add_parser("totp", help="Generate standard RFC 6238 2FA token")
    p_totp.add_argument("secret", type=str, help="Base32 TOTP secret")

    args = parser.parse_args()

    if args.command == "status":
        nav = FailoverNavigator()
        print("🌐 WebPilot Browser Status:")
        print(f"  • Primary Port ({nav.primary_port}): {'ONLINE' if nav.primary_engine.is_alive() else 'OFFLINE'}")
        print(f"  • Secondary Port ({nav.secondary_port}): {'ONLINE' if nav.secondary_engine.is_alive() else 'OFFLINE'}")

    elif args.command == "open":
        presets = load_presets()
        target_url = presets.get(args.target.lower(), args.target)
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        nav = FailoverNavigator()
        success, engine, details = nav.navigate(target_url)
        if success:
            print(f"✅ WebPilot navigated via {engine}: {details}")
        else:
            print(f"❌ Navigation failed: {details}")

    elif args.command == "totp":
        token = generate_totp(args.secret)
        print(f"🔑 Generated 2FA TOTP: {token}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
