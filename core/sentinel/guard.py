"""
SentinelGuard for TrueAgent: Integrated pre-push and secret protection engine.
"""

import os
import re
import json
from typing import List, Dict, Any


DEFAULT_SECRET_PATTERNS = {
    "private_key": r"-----BEGIN (?:RSA|OPENSSH|DSA|EC|PGP)?\s*PRIVATE KEY-----",
    "aws_access_key": r"\b(AKIA[0-9A-Z]{16})\b",
    "aws_sts_key": r"\b(ASIA[0-9A-Z]{16})\b",
    "github_pat": r"\b(gh[pousr]_[A-Za-z0-9_]{36,255}|github_pat_[0-9a-zA-Z_]{82})\b",
    "google_api_key": r"\b(AIza[0-9A-Za-z\-_]{35})\b",
    "openai_api_key": r"\b(sk-[a-zA-Z0-9]{48}|sk-proj-[a-zA-Z0-9_\-]{50,})\b",
    "anthropic_api_key": r"\b(sk-ant-[a-zA-Z0-9_\-]{32,})\b",
    "stripe_api_key": r"\b(sk_live_[0-9a-zA-Z]{24,}|rk_live_[0-9a-zA-Z]{24,})\b",
    "huggingface_token": r"\b(hf_[a-zA-Z0-9]{34,})\b",
    "generic_secret": r"""(?i)\b(?:api[_-]?key|secret[_-]?key|auth[_-]?token|access[_-]?token|password)\s*[:=]\s*['\"][A-Za-z0-9_\-!@#$%^&*]{8,128}['\"]""",
    "generic_secret_unquoted": r"""(?i)\b(?:api[_-]?key|secret[_-]?key|auth[_-]?token|access[_-]?token|password)\s*[:=]\s*[A-Za-z0-9_\-!@#$%^&*]{12,128}(?:\s|$)"""
}


class SentinelGuard:
    """Integrated security shield for TrueAgent."""

    def __init__(self, config_path: str = None):
        self.patterns = dict(DEFAULT_SECRET_PATTERNS)

    def scan_diff(self, diff_text: str) -> List[Dict[str, Any]]:
        """Scans git diff additions for secrets."""
        findings = []
        for line_no, line in enumerate(diff_text.splitlines(), start=1):
            if line.startswith("+") and not line.startswith("+++"):
                content = line[1:].strip()
                for cat, pat in self.patterns.items():
                    for match in re.finditer(pat, content):
                        matched = match.group(0)
                        masked = matched[:3] + "*" * (len(matched) - 6) + matched[-3:] if len(matched) > 8 else "***"
                        findings.append({
                            "line": line_no,
                            "rule": cat,
                            "type": cat,
                            "sample": masked
                        })
        return findings

    def scan_text(self, text: str, source_name: str = "text") -> List[Dict[str, Any]]:
        """Scans arbitrary text (file content) for secrets. Auto-detects diff format."""
        # Auto-detect unified diff format
        stripped = text.lstrip()
        if stripped.startswith("diff ") or stripped.startswith("--- "):
            return self.scan_diff(text)
        
        # Normal file scan - check ALL lines
        findings = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            content = line.strip()
            if not content:
                continue
            for cat, pat in self.patterns.items():
                for match in re.finditer(pat, content):
                    matched = match.group(0)
                    masked = matched[:3] + "*" * (len(matched) - 6) + matched[-3:] if len(matched) > 8 else "***"
                    findings.append({
                        "line": line_no,
                        "rule": cat,
                        "type": cat,
                        "sample": masked,
                        "source": source_name
                    })
        return findings

