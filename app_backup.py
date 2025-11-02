# ===============================================
# ⚡ THIÊN ĐẠO TOÀN QUYỀN v1.0 (Render Engine)
# -----------------------------------------------
# Xử lý toàn bộ quá trình: tu luyện - đột phá - linh khí - hiển thị.
# Kết nối plugin QCoreBridge (Minecraft) qua HTTP.
# -----------------------------------------------
# © Celestial QBIES Universe Engine
# ===============================================

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import math, time

app = FastAPI(title="Thiên Đạo Toàn Quyền Engine")

# =====================================================
# 🧬 MÔ HÌNH DỮ LIỆU
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
# ⚙️ CẤU HÌNH CẢNH GIỚI & MÀU LINH KHÍ
# =====================================================

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

PLAYER_STORE = {}

# =====================================================
# 🪶 HÀM HỖ TRỢ
# =====================================================

def make_action(act, target, **params):
    return Action(action=act, target=target, params=params)

def log(msg):
    print(f"[Thiên Đạo] {msg}")

# =====================================================
# 🌌 NHẬN SỰ KIỆN TỪ SERVER MINECRAFT
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

    # Cập nhật năng lượng
    if ev.type in ("tick", "tu_luyen"):
        gain = ev.energy or 1.0
        p["energy"] += gain
        p["karma"] = ev.karma or p["karma"]

    realm = get_realm_for_energy(p["energy"])
    p["realm_idx"] = next(i for i, r in enumerate(REALMS) if r["name"] == realm["name"])

    # Gửi cập nhật thanh linh khí
    actions.append(make_action(
        "set_ui", name,
        energy=p["energy"],
        required=REALMS[min(p["realm_idx"] + 1, len(REALMS) - 1)]["req"],
        realm=realm["name"],
        color=realm["color"],
        place_over_exp=True
    ))

    # Khi đủ linh khí đột phá
    next_realm = REALMS[p["realm_idx"] + 1] if p["realm_idx"] + 1 < len(REALMS) else None
    if next_realm and p["energy"] >= next_realm["req"]:
        log(f"{name} đủ linh khí đột phá {next_realm['name']}")
        # Tự động đột phá
        p["energy"] = 0.0
        p["realm_idx"] += 1
        new_realm = REALMS[p["realm_idx"]]
        actions.append(make_action("title", name, title="⚡ ĐỘT PHÁ!", subtitle=new_realm["name"]))
        actions.append(make_action("play_sound", name, sound="ENTITY_ENDER_DRAGON_GROWL", volume=1.0, pitch=0.8))
        actions.append(make_action("particle", name, type="DRAGON_BREATH", count=30, offset=[0, 2, 0]))

    # Khi tu luyện, hiển thị linh khí xoay quanh
    if ev.type == "tu_luyen":
        actions.append(make_action("particle", name, type="ENCHANTMENT_TABLE", count=12, offset=[0, 1.0, 0]))
        actions.append(make_action("play_sound", name, sound="BLOCK_ENCHANTMENT_TABLE_USE", volume=0.8, pitch=1.2))

    # Trả kết quả
    return ResponseModel(actions=actions)

# =====================================================
# ☯️ THIÊN ĐẠO HỎI Ý KIẾN (ví dụ tương tác người chơi)
# =====================================================

@app.post("/ask")
def ask_question(player: str, question: str):
    """Thiên Đạo gửi câu hỏi xuống người chơi (chat)."""
    return {
        "actions": [
            make_action("message", player, text=f"§d[Thiên Đạo] §f{question}").dict()
        ]
    }

# =====================================================
# 🔄 KIỂM TRA KẾT NỐI
# =====================================================

@app.get("/ping")
def ping():
    return {"ok": True, "time": time.time(), "realms": len(REALMS)}