
# dao_war.py — AI Chiến Thuật & Thiên Kiếp
from typing import Dict, Any

def strategic_tick(state: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal demo: if two factions close power, raise local conflict; if power gap huge, trigger omen (Kiếp)
    a = state.get("factionA_power", 40)
    b = state.get("factionB_power", 50)
    gap = abs(a-b)
    if gap < 10:
        return {"event":"border_skirmish", "intensity": "medium"}
    if max(a,b) > 90:
        return {"event":"heavenly_omen", "intensity":"high", "note":"Thiên Kiếp sắp tới"}
    return {"event":"calm", "intensity":"low"}
