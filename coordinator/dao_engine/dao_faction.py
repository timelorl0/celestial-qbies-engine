
# dao_faction.py — Đạo Thống / Tông môn
from typing import Dict, Any

_FACTIONS = {
    "ThienHoa": {"power": 55, "tenets":["Hỏa Diệt", "Tịnh Hóa"]},
    "UAm": {"power": 60, "tenets":["Bí Ảnh", "Ngự Ảnh"]}
}

def info(name: str) -> Dict[str, Any]:
    return {"name": name, "data": _FACTIONS.get(name, {"power":0, "tenets":[]})}

def all_factions() -> Dict[str, Any]:
    return {"factions": _FACTIONS}
