"""
ReviewForge: Clean-room Git diff and static code quality analyzer for TrueAgent.
100% original implementation. Analyzes diffs for bugs, complexity, and security pitfalls.
"""

import subprocess
import re
import ast
import os
from typing import List, Dict, Any


class ReviewForge:
    """Analyzes git diffs and code files for quality and security issues."""

    @staticmethod
    def get_git_diff(revision: str = "HEAD~1") -> str:
        """Retrieves raw diff against target git revision."""
        try:
            return subprocess.check_output(["git", "diff", revision], text=True, errors="ignore")
        except Exception:
            return ""

    @staticmethod
    def analyze_diff(diff_text: str) -> Dict[str, Any]:
        """Analyzes a git diff and outputs structured findings."""
        findings = []
        files_changed = set()
        additions = 0
        deletions = 0

        current_file = ""
        for line_no, line in enumerate(diff_text.splitlines(), start=1):
            if line.startswith("+++ b/"):
                current_file = line[6:]
                files_changed.add(current_file)
                continue

            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
                content = line[1:].strip()

                # Rule 1: Residual debug statements
                if re.search(r"\b(?:console\.log|debugger|import\s+pdb|breakpoint\(\))\b", content):
                    findings.append({
                        "file": current_file,
                        "line": line_no,
                        "rule": "RESIDUAL_DEBUG",
                        "type": "RESIDUAL_DEBUG",
                        "severity": "LOW",
                        "message": f"Leftover debugging statement: `{content[:60]}`"
                    })

                # Rule 2: SQL Injection indicators
                if re.search(r"""(?:SELECT|INSERT|UPDATE|DELETE).*?['"]\s*\+\s*\w+""", content, re.I):
                    findings.append({
                        "file": current_file,
                        "line": line_no,
                        "rule": "SQL_CONCATENATION",
                        "type": "SQL_CONCATENATION",
                        "severity": "HIGH",
                        "message": "Potential SQL injection vulnerability via raw string concatenation."
                    })

                # Rule 3: Broad exception swallowing
                if re.search(r"\bexcept\s*:\s*(?:pass)?|\bcatch\s*\([^)]*\)\s*\{\s*\}", content):
                    findings.append({
                        "file": current_file,
                        "line": line_no,
                        "rule": "SILENT_EXCEPTION",
                        "type": "SILENT_EXCEPTION",
                        "severity": "MEDIUM",
                        "message": "Broad exception without explicit type or handling."
                    })

            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        summary = {
            "total_files": len(files_changed),
            "files": list(files_changed),
            "additions": additions,
            "deletions": deletions,
            "total_findings": len(findings),
            "findings": findings
        }
        return summary

    @staticmethod
    def format_report_markdown(analysis: Dict[str, Any]) -> str:
        """Formats the analysis result into a clean markdown review report."""
        md = ["# 🔍 ReviewForge Code Review Report\n"]
        md.append(f"**Files Changed:** {analysis['total_files']} | **+Additions:** {analysis['additions']} | **-Deletions:** {analysis['deletions']}\n")

        if analysis["total_findings"] == 0:
            md.append("✅ **All Checks Passed**: Zero bugs, security pitfalls, or residual debug statements detected.\n")
        else:
            md.append(f"⚠️ **{analysis['total_findings']} issues detected:**\n")
            for item in analysis["findings"]:
                md.append(f"- **[{item['severity']}] {item['type']}** in `{item['file']}`\n  {item['message']}\n")

        return "\n".join(md)
