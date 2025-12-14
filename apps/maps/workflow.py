from __future__ import annotations

import re
from typing import Any, Dict, Optional


def route_followup(command: str, last_result: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    cmd = (command or "").strip().lower()
    if not cmd:
        return None

    m = re.search(r"(?:wybierz|select)\s*(\d+)", cmd)
    if m:
        return {"recognized": True, "app_type": "maps", "action": "select", "params": {"index": m.group(1)}}

    m = re.fullmatch(r"(\d+)", cmd)
    if m and isinstance(last_result, dict) and isinstance(last_result.get("results"), list) and last_result.get("results"):
        return {"recognized": True, "app_type": "maps", "action": "select", "params": {"index": m.group(1)}}

    if any(k in cmd for k in ["przybli", "powiększ", "powieksz", "zoom in", "zbliż", "zbliz"]):
        return {"recognized": True, "app_type": "maps", "action": "zoom_in", "params": {}}

    if any(k in cmd for k in ["oddal", "pomniejsz", "zoom out", "zmniejsz"]):
        return {"recognized": True, "app_type": "maps", "action": "zoom_out", "params": {}}

    if ("reset" in cmd and "zoom" in cmd) or cmd in {"reset", "resetuj", "resetuj powiększenie", "resetuj powiekszenie"}:
        return {"recognized": True, "app_type": "maps", "action": "zoom_reset", "params": {}}

    return None


def preprocess_intent(
    *,
    intent: Dict[str, Any],
    last_result: Optional[Dict[str, Any]] = None,
    command: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not isinstance(intent, dict) or intent.get("app_type") != "maps":
        return intent

    updated = dict(intent)
    params = updated.get("params")
    if not isinstance(params, dict):
        params = {}

    extra = extra or {}
    client_ip = extra.get("client_ip")
    if client_ip and params.get("_client_ip") is None:
        params["_client_ip"] = client_ip

    action = updated.get("action")

    if action == "select":
        idx_raw = params.get("index")
        if idx_raw is not None:
            m = re.search(r"\d+", str(idx_raw))
            if m:
                params["index"] = m.group(0)

    if action in ["select", "zoom_in", "zoom_out", "zoom_reset"] and isinstance(last_result, dict):
        if not str(params.get("query") or "").strip():
            prev_query = str(last_result.get("query") or "").strip()
            if prev_query:
                params["query"] = prev_query

        if isinstance(last_result.get("results"), list) and not isinstance(params.get("results"), list):
            params["results"] = last_result.get("results")

        if isinstance(last_result.get("user_location"), dict) and not isinstance(params.get("user_location"), dict):
            params["user_location"] = last_result.get("user_location")

        if last_result.get("map_delta") is not None and params.get("map_delta") is None:
            params["map_delta"] = last_result.get("map_delta")

        if action != "select":
            if (
                last_result.get("selected_index") is not None
                and params.get("selected_index") is None
                and params.get("index") is None
            ):
                params["selected_index"] = last_result.get("selected_index")

    updated["params"] = params
    return updated
