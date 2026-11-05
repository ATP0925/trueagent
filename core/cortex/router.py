"""
CortexRouter: Hardware-Aware Decision and Resource Router for TrueAgent.
Dynamically resolves paths, monitors system memory, and determines compute strategy.
"""

import os
import sys
import json
import ctypes
from typing import Dict, Any, Tuple


class SystemMemoryInfo:
    """Retrieves real-time OS memory metrics without third-party dependencies."""

    @staticmethod
    def get_available_ram_gb() -> float:
        """Returns available physical RAM in gigabytes."""
        if sys.platform == "win32":
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return stat.ullAvailPhys / (1024 ** 3)
        else:
            # POSIX / Linux / Darwin fallback
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if "MemAvailable" in line:
                            kb = int(line.split()[1])
                            return kb / (1024 ** 2)
            except Exception:
                pass
            return 8.0  # safe default


class CortexRouter:
    """Routes execution targets, browser engines, and compute strategies."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)

    def _load_config(self, path: str = None) -> Dict[str, Any]:
        candidates = [
            path,
            os.path.join(os.getcwd(), "trueagent.config.json"),
            os.path.expanduser("~/.trueagent.json"),
            os.path.expanduser("~/.config/trueagent/trueagent.config.json")
        ]
        for c in candidates:
            if c and os.path.exists(c):
                try:
                    with open(c, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return {
            "persona": {"callsign": "Operator"},
            "browser": {"primary_port": 9222, "secondary_port": 9223},
            "hardware": {"ram_cloud_threshold_gb": 4.0}
        }

    def get_user_callsign(self) -> str:
        """Returns configured user title/callsign (generic, no hardcoded Boss)."""
        return self.config.get("persona", {}).get("callsign", "Operator")

    def route_compute(self, task_memory_intensity: str = "normal") -> Tuple[str, str]:
        """
        Determines whether a task should run locally or be delegated to cloud APIs.
        Returns: (target_route, reason)
        """
        threshold = self.config.get("hardware", {}).get("ram_cloud_threshold_gb", 4.0)
        avail_ram = SystemMemoryInfo.get_available_ram_gb()

        if task_memory_intensity in ["heavy", "llm_eval", "bundle_build"] and avail_ram < threshold:
            return "CLOUD_API", f"Available RAM ({avail_ram:.1f} GB) is below safety threshold ({threshold} GB). Routing to Cloud API."
        
        return "LOCAL", f"Available RAM ({avail_ram:.1f} GB) is adequate for local execution."

    def resolve_browser_port(self, browser_type: str = "primary") -> int:
        """Retrieves configured remote debugging port."""
        browser_cfg = self.config.get("browser", {})
        if browser_type == "secondary":
            return browser_cfg.get("secondary_port", 9223)
        return browser_cfg.get("primary_port", 9222)

    def get_workspace_root(self) -> str:
        """Returns current dynamic workspace directory."""
        return os.getcwd()
