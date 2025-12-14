from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple


_DIACRITICS = str.maketrans(
    {
        "ą": "a",
        "ć": "c",
        "ę": "e",
        "ł": "l",
        "ń": "n",
        "ó": "o",
        "ś": "s",
        "ż": "z",
        "ź": "z",
    }
)


def _normalize(text: str) -> str:
    return (text or "").lower().translate(_DIACRITICS)


_MONTHS: Dict[str, Tuple[int, str]] = {
    "styczen": (1, "styczeń"),
    "stycznia": (1, "styczeń"),
    "luty": (2, "luty"),
    "lutego": (2, "luty"),
    "marzec": (3, "marzec"),
    "marca": (3, "marzec"),
    "kwiecien": (4, "kwiecień"),
    "kwietnia": (4, "kwiecień"),
    "maj": (5, "maj"),
    "maja": (5, "maj"),
    "czerwiec": (6, "czerwiec"),
    "czerwca": (6, "czerwiec"),
    "lipiec": (7, "lipiec"),
    "lipca": (7, "lipiec"),
    "sierpien": (8, "sierpień"),
    "sierpnia": (8, "sierpień"),
    "wrzesien": (9, "wrzesień"),
    "wrzesnia": (9, "wrzesień"),
    "pazdziernik": (10, "październik"),
    "pazdziernika": (10, "październik"),
    "listopad": (11, "listopad"),
    "listopada": (11, "listopad"),
    "grudzien": (12, "grudzień"),
    "grudnia": (12, "grudzień"),
}


def route_followup(command: str, last_result: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    cmd_norm = _normalize(command)
    if not cmd_norm.strip():
        return None

    year = None
    m = re.search(r"\b(20\d{2})\b", cmd_norm)
    if m:
        year = int(m.group(1))

    for token, (month, month_name) in _MONTHS.items():
        if re.search(rf"\b{re.escape(token)}\b", cmd_norm):
            return {
                "recognized": True,
                "app_type": "sales",
                "action": "show_dashboard",
                "params": {"month": month, "month_name": month_name, "year": year},
            }

    m = re.search(r"\bza\s+(\d{1,2})\b", cmd_norm)
    if m:
        month = int(m.group(1))
        if 1 <= month <= 12:
            return {
                "recognized": True,
                "app_type": "sales",
                "action": "show_dashboard",
                "params": {"month": month, "month_name": None, "year": year},
            }

    return None
