# ===============================================
# ⚡ CELESTIAL QBIES ENGINE (Render - Thiên Đạo)
# -----------------------------------------------
# Tích hợp Thiên Đạo với Falix (Địa) và hệ thống plugin auto-sync.
# -----------------------------------------------
# © Celestial QBIES Universe Engine
# ===============================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os, json, time, random, re, threading

app = FastAPI(title="Celestial QBIES Render Engine")

# =====================================================
# 🧬 CẤU HÌNH & DỮ LIỆU
# =====================================================
PLAYER_STORE = {}

REALMS = [
    {"name": "Phàm Nhân", "req": 0, "color": "§7"},
    {"name": "Nhập Môn", "req": 50, "color": "§9"},
    {"name": "Trúc Cơ", "req": 200, "color": "§a"},
    {"name": "Ngưng Tuyền", "req": 800, "color": "§e"},
    {"name": "Kim Đan", "req": 2500, "color": "§6"},
    {"name": "Nguyên Anh", "req": 6000, "color": "§d"},
    {"name": "Hóa Thần", "req": 15000, "color": "§5"},
]

def get_realm_for_energy(e):
    current = REALMS[0]
    for r in REALMS:
        if e >= r["req"]:
            current = r
        else:
            break
    return current


# =====================================================
# 🧠 CÁC MÔ HÌNH DỮ LIỆU
# =====================================================
class PlayerEvent(BaseModel):
    type: str
    player: str
    realm: Optional[str] = None
    energy: float = 0.0
    karma: float = 0.0
    position: Optional[List[float]] = None
    extra: Optional[Dict[str, Any]] = None


class Action(BaseModel):
    action: str
    target: str
    params: Dict[str, Any] = {}


class ResponseModel(BaseModel):
    actions: List[Action] = []


# =====================================================
# 🌌 HÀM HỖ TRỢ
# =====================================================
def make_action(act, target, **params):
    return Action(action=act, target=target, params=params)

def log(msg):
    print(f"[Thiên Đạo] {msg}")


# =====================================================
# ⚙️ API XỬ LÝ SỰ KIỆN
# =====================================================
@app.post("/process_event", response_model=ResponseModel)
def process_event(ev: PlayerEvent):
    name = ev.player
    p = PLAYER_STORE.setdefault(name, {
        "energy": 0.0,
        "realm_idx": 0,
        "karma": 0.0,
        "last_tick": time.time(),
        "auto": True
    })

    actions = []

    if ev.type in ("tick", "tu_luyen"):
        gain = ev.energy or random.uniform(0.8, 1.4)
        p["energy"] += gain
        p["karma"] = ev.karma or p["karma"]

    realm = get_realm_for_energy(p["energy"])
    p["realm_idx"] = next(i for i, r in enumerate(REALMS) if r["name"] == realm["name"])

    actions.append(make_action(
        "set_ui", name,
        energy=round(p["energy"], 1),
        required=REALMS[min(p["realm_idx"] + 1, len(REALMS) - 1)]["req"],
        realm=realm["name"],
        color=realm["color"],
        place_over_exp=True
    ))

    next_realm = REALMS[p["realm_idx"] + 1] if p["realm_idx"] + 1 < len(REALMS) else None
    if next_realm and p["energy"] >= next_realm["req"]:
        log(f"{name} đủ linh khí đột phá {next_realm['name']}")
        p["energy"] = 0.0
        p["realm_idx"] += 1
        new_realm = REALMS[p["realm_idx"]]
        actions.append(make_action("title", name, title="⚡ ĐỘT PHÁ!", subtitle=new_realm["name"]))
        actions.append(make_action("play_sound", name, sound="ENTITY_PLAYER_LEVELUP", volume=1.2, pitch=0.6))
        actions.append(make_action("particle", name, type="TOTEM", count=60, offset=[0, 1.5, 0]))
        actions.append(make_action("auto_continue", name, realm=new_realm["name"]))

    if ev.type == "tu_luyen":
        actions.append(make_action("particle", name, type="ENCHANTMENT_TABLE", count=16, offset=[0, 1.0, 0]))
        actions.append(make_action("play_sound", name, sound="BLOCK_ENCHANTMENT_TABLE_USE", volume=0.7, pitch=1.2))

    return ResponseModel(actions=actions)


# =====================================================
# ☯️ KIỂM TRA HỆ THỐNG
# =====================================================
@app.get("/ping")
def ping():
    return {"ok": True, "time": time.time(), "realms": len(REALMS), "players": len(PLAYER_STORE)}


# =====================================================
# 🌍 API: CUNG CẤP MÃ QCoreBridge.java CHO FALIX
# =====================================================
@app.get("/api/plugin/qcorebridge/latest", response_class=PlainTextResponse)
def get_latest_qcorebridge():
    """
    Cung cấp mã QCoreBridge.java mới nhất cho Falix tải và biên dịch tự động.
    Tự động lọc bỏ dòng trùng lặp.
    """
    src_path = os.path.join("coordinator", "sync_data", "QCoreBridge.java")

    if not os.path.exists(src_path):
        return "// ❌ Không tìm thấy file QCoreBridge.java trên server Render.\n"

    try:
        with open(src_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        seen = set()
        filtered = []
        for line in lines:
            key = re.sub(r"\s+", "", line)
            if key not in seen:
                filtered.append(line)
                seen.add(key)

        code = "".join(filtered)
        header = "// ✅ QCoreBridge.java (Auto-synced from Render)\n"
        return header + code

    except Exception as e:
        return f"// ⚠️ Lỗi khi đọc file: {e}\n"


# =====================================================
# 🧠 TỰ LƯU TRẠNG THÁI
# =====================================================
SNAPSHOT_DIR = "coordinator/cache_data/snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def auto_snapshot():
    while True:
        try:
            snap_file = os.path.join(SNAPSHOT_DIR, "universe.qbie")
            with open(snap_file, "w", encoding="utf-8") as f:
                json.dump(PLAYER_STORE, f, ensure_ascii=False, indent=2)
            print(f"💾 [Fractal] Snapshot saved: {snap_file}")
        except Exception as e:
            print(f"⚠️ Snapshot error: {e}")
        time.sleep(600)

threading.Thread(target=auto_snapshot, daemon=True).start()

print("🌌 [Thiên Đạo] Render Engine sẵn sàng.")