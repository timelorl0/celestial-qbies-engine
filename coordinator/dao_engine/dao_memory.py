
# dao_memory.py — Ký ức tiền kiếp
from typing import Dict, Any

# In real build, map to QBIES. Here, simple in-memory store (demo).
_MEM = {}

def read_memory(soul_id: str) -> Dict[str, Any]:
    return _MEM.get(soul_id, {"memories":[]})

def write_memory(soul_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    cur = _MEM.get(soul_id, {"memories":[]})
    cur["memories"].append(data)
    _MEM[soul_id] = cur
    return {"ok": True, "count": len(cur["memories"])}
