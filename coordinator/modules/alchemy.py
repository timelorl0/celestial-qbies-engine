# coordinator/modules/alchemy.py
"""
Alchemy: stub luyện đan — input linh thảo -> output đan (sơ khung)
"""
def init(app=None, config=None):
    print("[Alchemy] ready")

def craft_pill(recipe, materials):
    # dummy logic: nếu đủ materials -> success pill
    missing = [m for m in recipe.get("requires",[]) if m not in materials]
    if missing:
        return {"ok":False,"missing":missing}
    return {"ok":True,"pill":{"name":recipe.get("name","Unknown Pill"), "power": recipe.get("power",1)}}