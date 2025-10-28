
# dao_reincarnate.py — Luân hồi
from typing import Dict, Any
import random

def reincarnate(soul: Dict[str, Any]) -> Dict[str, Any]:
    # Demo: decide spawn realm by karma
    karma = soul.get("karma", 0)
    if karma >= 50:
        realm = "Thượng Giới"
        bonus = {"buff":"light_bless", "duration_sec": 120}
    elif karma <= -30:
        realm = "Hư Vô Giới"
        bonus = {"debuff":"shadow_chain", "duration_sec": 120}
    else:
        realm = "Nhân Giới"
        bonus = {}
    # random position (demo)
    pos = {"x": random.randint(-100,100),"y": 70, "z": random.randint(-100,100)}
    return {"realm": realm, "pos": pos, "bonus": bonus, "message": f"Tái sinh tại {realm}."}
