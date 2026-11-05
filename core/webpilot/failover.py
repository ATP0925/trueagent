"""
Failover Navigator for WebPilot:
Directs navigation to Primary browser; auto-cascades to Secondary browser if blocked.
Ports and browser names are read from trueagent.config.json.
"""

import os
import json
import time
from typing import Tuple, Dict, Any
from .cdp_engine import CDPEngine


class FailoverNavigator:
    """Manages resilient multi-browser navigation."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        b_cfg = self.config.get("browser", {})
        self.primary_port = b_cfg.get("primary_port", 9222)
        self.secondary_port = b_cfg.get("secondary_port", 9223)
        self.primary_engine = CDPEngine(port=self.primary_port)
        self.secondary_engine = CDPEngine(port=self.secondary_port)

    def _load_config(self, path: str = None) -> Dict[str, Any]:
        candidates = [
            path,
            os.path.join(os.getcwd(), "trueagent.config.json"),
            os.path.expanduser("~/.trueagent.json")
        ]
        for c in candidates:
            if c and os.path.exists(c):
                try:
                    with open(c, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return {"browser": {"primary_port": 9222, "secondary_port": 9223}}

    def navigate(self, url: str) -> Tuple[bool, str, str]:
        """
        Navigates to URL.
        Returns: (success, engine_used, details)
        """
        # Try Primary Engine
        if self.primary_engine.is_alive():
            tab = self.primary_engine.open_new_tab(url)
            if tab:
                return True, f"Primary (Port {self.primary_port})", f"Opened tab {tab.get('id')} at {url}"

        # If primary fails or is offline, cascade to Secondary
        if self.secondary_engine.is_alive():
            tab = self.secondary_engine.open_new_tab(url)
            if tab:
                return True, f"Secondary Failover (Port {self.secondary_port})", f"Cascade successful to secondary engine: {tab.get('id')}"

        return False, "None", f"Neither primary (port {self.primary_port}) nor secondary (port {self.secondary_port}) browser is reachable."
