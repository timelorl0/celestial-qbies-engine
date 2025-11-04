# coordinator/modules/attributes.py
"""
Attributes: tư chất, chỉ số cơ bản cho nhân vật.
"""
def init(app=None, config=None):
    print("[Attributes] module ready")

def base_stats_for(talent_level=1):
    return {
        "vitality": 10 * talent_level,
        "qi_capacity": 100 * talent_level,
        "mental": 5 * talent_level
    }

def apply_stat_buff(player_state, buff):
    st = player_state.setdefault("meta", {})
    buffs = st.setdefault("buffs", [])
    buffs.append(buff)
    return st