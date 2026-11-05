"""
CDP Engine for WebPilot: Lightweight DevTools Protocol client via standard library.
"""

import json
import urllib.request
from typing import List, Dict, Any, Optional


class CDPEngine:
    """Connects to any Chromium browser with an open remote debugging port."""

    def __init__(self, port: int = 9222, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self.base_url = f"http://{host}:{port}"

    def is_alive(self) -> bool:
        """Verifies if the remote debugging port is reachable."""
        try:
            req = urllib.request.Request(f"{self.base_url}/json/version")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_tabs(self) -> List[Dict[str, Any]]:
        """Retrieves list of active browser tabs."""
        try:
            req = urllib.request.Request(f"{self.base_url}/json/list")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return []

    def open_new_tab(self, url: str) -> Optional[Dict[str, Any]]:
        """Opens a new tab targeting the specified URL."""
        try:
            target_url = f"{self.base_url}/json/new?{urllib.parse.quote(url, safe=':/?=&')}"
            req = urllib.request.Request(target_url, method="PUT")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    def close_tab(self, tab_id: str) -> bool:
        """Closes a specific tab."""
        try:
            req = urllib.request.Request(f"{self.base_url}/json/close/{tab_id}")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

