# ===============================================
# ⚡ THIÊN ĐẠO TOÀN QUYỀN v1.0 (Render Engine)
# -----------------------------------------------
# Hòa nhập toàn bộ vào hệ thống Celestial QBIES gốc.
# Xử lý: tu luyện - đột phá - hiển thị - linh khí - âm thanh - tương tác.
# Liên kết plugin QCoreBridge (Minecraft).
# -----------------------------------------------
# © Celestial QBIES Universe Engine
# ===============================================

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time, random, os, json, threading, requests
from pathlib import Path

# =====================================================
# ⚙️ KHỞI TẠO HỆ THỐNG
# =====================================================

try:
    app  # nếu app đã được tạo ở nơi khác
except NameError:
    app = FastAPI(title="Celestial QBIES Unified Engine")

BASE_DIR = Path(__file__).parent

# ❗ ĐỔI THƯ MỤC CACHE để tránh đụng tên file `cache`
SNAPSHOT_ROOT = BASE_DIR / "cache_data"
SNAPSHOT_DIR = SNAPSHOT_ROOT / "snapshots"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOT_FILE = SNAPSHOT_DIR / "universe.qbie"

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
FALIX_API = os.environ.get("FALIX_API", "http://localhost:25575/command")
AUTO_RELOAD_SECRET = os.environ.get("AUTO_RELOAD_SECRET", "celestial-secret")

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

def get_realm_for_energy(e: float):
    current = REALMS[0]
    for r in REALMS:
        if e >= r["req"]:
            current = r
        else:
            break
    return current

PLAYER_STORE: Dict[str, Dict[str, Any]] = {}

# =====================================================
# 🪶 HÀM HỖ TRỢ
# =====================================================

def make_action(act: str, target: str, **params):
    return Action(action=act, target=target, params=params)

def log(msg: str):
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
        "auto": True,
    })

    actions: List[Action] = []

    # Cập nhật năng lượng / karma
    if ev.type in ("tick", "tu_luyen"):
        gain = ev.energy or random.uniform(0.8, 1.4)
        p["energy"] += gain
        p["karma"] = ev.karma or p["karma"]

    # Cảnh giới hiện tại
    realm = get_realm_for_energy(p["energy"])
    p["realm_idx"] = next(i for i, r in enumerate(REALMS) if r["name"] == realm["name"])

    # UI linh khí
    actions.append(make_action(
        "set_ui", name,
        energy=round(p["energy"], 1),
        required=REALMS[min(p["realm_idx"] + 1, len(REALMS) - 1)]["req"],
        realm=realm["name"],
        color=realm["color"],
        place_over_exp=True,
    ))

    # Đột phá
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

    # Hiệu ứng khi tu luyện chủ động
    if ev.type == "tu_luyen":
        actions.append(make_action("particle", name, type="ENCHANTMENT_TABLE", count=16, offset=[0, 1.0, 0]))
        actions.append(make_action("play_sound", name, sound="BLOCK_ENCHANTMENT_TABLE_USE", volume=0.7, pitch=1.2))

    return ResponseModel(actions=actions)

# =====================================================
# ☯️ THIÊN ĐẠO HỎI Ý KIẾN
# =====================================================

@app.post("/ask")
def ask_question(player: str, question: str):
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
    return {
        "ok": True,
        "time": time.time(),
        "realms": len(REALMS),
        "players": len(PLAYER_STORE),
    }

# =====================================================
# 💾 TỰ ĐỘNG SNAPSHOT .QBIE
# =====================================================

def save_snapshot():
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "energy_map": {p: v["energy"] for p, v in PLAYER_STORE.items()},
        "realm_map": {p: REALMS[v["realm_idx"]]["name"] for p, v in PLAYER_STORE.items()},
        "players": list(PLAYER_STORE.keys()),
    }
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 [Fractal] Snapshot saved: {SNAPSHOT_FILE}")

def auto_snapshot():
    while True:
        save_snapshot()
        time.sleep(600)  # 10 phút

threading.Thread(target=auto_snapshot, daemon=True).start()

# =====================================================
# 💓 FALIX HEARTBEAT
# =====================================================

def falix_heartbeat():
    while True:
        time.sleep(30)
        try:
            requests.post(FALIX_API, json={"command": "list"})
            print("💓 [Heartbeat] Sent to Falix.")
        except Exception as e:
            print("⚠️ [Falix] Heartbeat failed:", e)

threading.Thread(target=falix_heartbeat, daemon=True).start()

# =====================================================
# 🖥️ DASHBOARD
# =====================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    html = f"""
    <html>
    <head>
      <title>Celestial Dashboard</title>
      <meta http-equiv="refresh" content="15">
      <style>
        body {{ background-color: #0b0b0b; color: #00ffcc; font-family: monospace; text-align: center; }}
        .card {{ background: #111; padding: 20px; margin: 20px auto; width: 60%; border-radius: 10px; }}
      </style>
    </head>
    <body>
      <h1>🌌 Celestial Engine Dashboard</h1>
      <div class="card">
        <p>💾 Snapshot: {SNAPSHOT_FILE.name}</p>
        <p>🕒 {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>👥 Players: {len(PLAYER_STORE)}</p>
        <p>💓 Heartbeat: Active</p>
      </div>
      <footer>⚡ Celestial QBIES Universe Engine</footer>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# =====================================================
# 🏁 ROOT
# =====================================================

@app.get("/")
def root():
    return {"msg": "Celestial QBIES Unified Engine Active", "time": time.time()}
