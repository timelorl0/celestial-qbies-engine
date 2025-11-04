# coordinator/modules/talisman.py
"""
Talisman: tạo phù lục, apply effect (stub)
"""
def init(app=None, config=None):
    print("[Talisman] ready")

def forge_talisman(formula, sigils):
    # placeholder: return talisman object
    return {"ok":True, "talisman": {"name": formula.get("name","phù vô danh"), "sigils": len(sigils)}}