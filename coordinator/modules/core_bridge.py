# coordinator/modules/core_bridge.py
"""
Core bridge: API helper để plugin Minecraft gọi Celestial Engine.
Đảm nhiệm: lưu state player, trả về hành động (actions) cho plugin xử lý.
"""
import time, json, os
PLAYER_STORE = {}
DEFAULT_REALMS = ["Phàm Nhân", "Nhập Môn", "Luyện Khí", "Trúc Cơ", "Kết Đan", "Nguyên Anh", "Hóa Thần", "Luyện Hư", "Hợp Thể", "Đại Thừa", "Độ Kiếp"]
REALM_THRESHOLDS = [0,50,200,800,3000,8000,20000,50000,120000,300000,1000000]

def init(app=None, config=None):
    print("[CoreBridge] ready")

def get_player(name):
    return PLAYER_STORE.setdefault(name, {"energy":0.0,"realm":"Phàm Nhân","path":None,"meta":{}})

def tick(player_name, energy_gain=1.0):
    p = get_player(player_name)
    p["energy"] = p.get("energy",0.0) + float(energy_gain)
    p["last"] = time.time()
    # determine realm
    idx = 0
    for i, t in enumerate(REALM_THRESHOLDS):
        if p["energy"] >= t:
            idx = i
    p["realm"] = DEFAULT_REALMS[idx]
    actions = []
    # breakthrough check (if enough for next)
    if idx + 1 < len(REALM_THRESHOLDS) and p["energy"] >= REALM_THRESHOLDS[idx+1]:
        p["energy"] = 0.0
        p["realm"] = DEFAULT_REALMS[idx+1]
        actions.append({"action":"title","title":"⚡ ĐỘT PHÁ!","subtitle":p["realm"]})
        actions.append({"action":"sound","sound":"ENTITY_PLAYER_LEVELUP"})
        actions.append({"action":"particle","type":"TOTEM","count":60})
    return {"player":player_name,"realm":p["realm"],"energy":round(p["energy"],2),"actions":actions}

def choose_path(player_name, path_id):
    p = get_player(player_name)
    p["path"] = path_id
    return {"ok":True,"path":path_id}