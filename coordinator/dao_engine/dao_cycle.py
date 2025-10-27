
# dao_cycle.py — Chu kỳ Thiên Kiếp
from typing import Dict, Any

_cycle = {"chaos": 0, "age": 0, "cycle_id": 1}

def tick(delta:int=1) -> Dict[str, Any]:
    _cycle["age"] += delta
    _cycle["chaos"] = min(100, _cycle["chaos"] + delta//10)
    return dict(_cycle)

def trigger_if_ready() -> Dict[str, Any]:
    if _cycle["chaos"] >= 80 or _cycle["age"] >= 600:
        _cycle["cycle_id"] += 1
        _cycle["age"] = 0
        _cycle["chaos"] = 10
        return {"rebirth": True, "cycle_id": _cycle["cycle_id"], "message":"Thiên Kiếp hoàn thành — thế giới tái sinh."}
    return {"rebirth": False}
