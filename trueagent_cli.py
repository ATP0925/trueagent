#!/usr/bin/env python3
"""
TrueAgent Universal CLI Runner
Master unified entrypoint for TrueAgent: Cortex Routing, ReviewForge, SentinelGuard, and VoxCore.
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from core.cortex.router import CortexRouter, SystemMemoryInfo
from core.sentinel.guard import SentinelGuard
from core.reviewforge.reviewer import ReviewForge
from core.webpilot.totp import generate_totp
from core.voxcore.speak import sanitize_text

def cmd_status():
    router = CortexRouter()
    ram_gb = SystemMemoryInfo.get_available_ram_gb()
    callsign = router.get_user_callsign()
    p_port = router.resolve_browser_port("primary")
    s_port = router.resolve_browser_port("secondary")

    print("=" * 65)
    print(" 🚀 TRUEAGENT UNIVERSAL SYSTEM STATUS")
    print("=" * 65)
    print(f"[*] User Callsign      : {callsign}")
    print(f"[*] Available Physical : {ram_gb:.2f} GB RAM")
    print(f"[*] Primary CDP Port   : {p_port}")
    print(f"[*] Secondary CDP Port : {s_port}")
    print("[*] Security Shield    : ACTIVE (SentinelGuard v1.2)")
    print("[*] Code Review Forge  : READY (ReviewForge v1.1)")
    print("[*] Duplex VoxCore     : DSP Highpass Filter Active")
    print("=" * 65)

def cmd_scan(args):
    guard = SentinelGuard()
    if os.path.isfile(args.file):
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            diff_text = f.read()
    else:
        diff_text = args.file

    findings = guard.scan_diff(diff_text)
    print(f"🛡️ SentinelGuard Scan Results ({len(findings)} findings):")
    if not findings:
        print("  ✅ Clean! Zero secrets or credentials detected.")
    else:
        for f in findings:
            print(f"  ❌ Line {f.get('line')}: {f.get('type')} -> {f.get('sample')}")
        sys.exit(1)

def cmd_totp(args):
    code = generate_totp(args.secret)
    print(f"🔑 Generated RFC 6238 TOTP Code: {code}")

def cmd_review(args):
    if os.path.isfile(args.file):
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            diff_text = f.read()
    else:
        diff_text = args.file

    res = ReviewForge.analyze_diff(diff_text)
    print(f"🐇 ReviewForge Code Review: {res.get('total_findings')} finding(s) across {res.get('total_files')} file(s).")
    for f in res.get("findings", []):
        print(f"  [{f.get('severity')}] Line {f.get('line')}: {f.get('rule')} -> {f.get('message')}")

def main():
    parser = argparse.ArgumentParser(description="TrueAgent Unified CLI Runner")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Display system status and memory metrics")

    p_scan = sub.add_parser("scan", help="Scan diff or file for secrets with SentinelGuard")
    p_scan.add_argument("file", help="Path to diff/file or raw text")

    p_totp = sub.add_parser("totp", help="Generate 6-digit TOTP code")
    p_totp.add_argument("secret", help="Base32 2FA secret key")

    p_rev = sub.add_parser("review", help="Review diff for code quality with ReviewForge")
    p_rev.add_argument("file", help="Path to diff file")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "scan":
        cmd_scan(args)
    elif args.command == "totp":
        cmd_totp(args)
    elif args.command == "review":
        cmd_review(args)
    else:
        cmd_status()

if __name__ == "__main__":
    main()
