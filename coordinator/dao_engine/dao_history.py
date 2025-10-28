
# dao_history.py — Ghi Thiên Sử
from typing import Dict, Any, List

_HISTORY: List[Dict[str, Any]] = []

def record(evt: Dict[str, Any]) -> Dict[str, Any]:
    _HISTORY.append(evt)
    return {"ok": True, "size": len(_HISTORY)}

def recent(n: int = 10) -> Dict[str, Any]:
    return {"events": _HISTORY[-n:]}
