# coordinator/modules/forge.py
"""
Forge: luyện khí / tạo pháp khí (stub)
"""
def init(app=None, config=None):
    print("[Forge] ready")

def craft_artifact(template, components):
    # simple validation
    ok = all(c in components for c in template.get("requires",[]))
    if not ok:
        return {"ok":False}
    return {"ok":True,"artifact": {"id": template.get("id","artifact_x"), "tier": template.get("tier",1)}}