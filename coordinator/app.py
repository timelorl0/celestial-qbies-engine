# ===============================================
# 🌌 CELESTIAL QBIES – THIÊN ĐỊA HỢP NHẤT v1.0
# -----------------------------------------------
# Thiên (Render): Lõi trí tuệ, tu luyện, snapshot, dashboard
# Địa (Falix): Server Minecraft, gửi sự kiện & nhận lệnh
# Snapshot: universe.qbie – trí nhớ vũ trụ
# -----------------------------------------------
# © Celestial QBIES Universe Engine
# ===============================================

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
import time, random, os, json, threading, requests

# =====================================================
# ⚙️ KHỞI TẠO THIÊN ĐẠO (RENDER ENGINE)
# =====================================================

try:
    app  # nếu app đã tồn tại
except NameError:
    app = FastAPI(title="Celestial QBIES Unified Engine")

BASE_DIR = Path(__file__).parent

# Thư mục lưu snapshot vũ trụ
SNAPSHOT_ROOT = BASE_DIR / "cache_data"
SNAPSHOT_DIR = SNAPSHOT_ROOT / "snapshots"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOT_FILE = SNAPSHOT_DIR / "universe.qbie"

# Cấu hình liên kết Địa (Falix) – KHÔNG dùng link timer client
FALIX_API = os.environ.get("FALIX_API", "").strip()
# Ví dụ hợp lệ:
# FALIX_API = "http://your-falix-server-or-proxy/status"

PLAYER_STORE: Dict[str, Dict[str, Any]] = {}

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
# ⚙️ CẤU HÌNH CẢNH GIỚI & LINH KHÍ
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

def get_realm_for_energy(e: float) -> Dict[str, Any]:
    current = REALMS[0]
    for r in REALMS:
        if e >= r["req"]:
            current = r
        else:
            break
    return current

def make_action(act: str, target: str, **params) -> Action:
    return Action(action=act, target=target, params=params)

def log(msg: str):
    print(f"[Thiên Đạo] {msg}")

# =====================================================
# 🌌 API: NHẬN SỰ KIỆN TỪ ĐỊA (FALIX / MINECRAFT)
# =====================================================

@app.post("/process_event", response_model=ResponseModel)
def process_event(ev: PlayerEvent):
    """
    Plugin trên Falix gửi sự kiện dạng JSON:
    {
      "type": "tu_luyen" | "tick" | "khac",
      "player": "TenNguoiChoi",
      "energy": 3.5,
      "karma": 0.1
    }
    """
    name = ev.player
    p = PLAYER_STORE.setdefault(name, {
        "energy": 0.0,
        "realm_idx": 0,
        "karma": 0.0,
        "last_tick": time.time(),
        "auto": True,
    })

    actions: List[Action] = []

    # Cập nhật năng lượng
    if ev.type in ("tick", "tu_luyen"):
        gain = ev.energy or random.uniform(0.8, 1.4)
        p["energy"] += gain
        p["karma"] = ev.karma or p["karma"]
        p["last_tick"] = time.time()

    realm = get_realm_for_energy(p["energy"])
    p["realm_idx"] = next(i for i, r in enumerate(REALMS) if r["name"] == realm["name"])

    # UI linh khí đặt lên thanh exp
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
        actions += [
            make_action("title", name, title="⚡ ĐỘT PHÁ!", subtitle=new_realm["name"]),
            make_action("play_sound", name, sound="ENTITY_PLAYER_LEVELUP", volume=1.2, pitch=0.6),
            make_action("particle", name, type="TOTEM", count=60, offset=[0, 1.5, 0]),
            make_action("auto_continue", name, realm=new_realm["name"]),
        ]

    # Hiệu ứng tu luyện chủ động
    if ev.type == "tu_luyen":
        actions += [
            make_action("particle", name, type="ENCHANTMENT_TABLE", count=16, offset=[0, 1.0, 0]),
            make_action("play_sound", name, sound="BLOCK_ENCHANTMENT_TABLE_USE", volume=0.7, pitch=1.2),
        ]

    return ResponseModel(actions=actions)

# =====================================================
# ☯️ API: PING / STATUS
# =====================================================

@app.get("/ping")
def ping():
    return {
        "ok": True,
        "time": time.time(),
        "players": len(PLAYER_STORE),
        "realms": len(REALMS),
    }

@app.get("/status")
def status():
    return {
        "engine": "Celestial QBIES Unified Engine",
        "snapshot": str(SNAPSHOT_FILE),
        "players": list(PLAYER_STORE.keys()),
        "falix_api_configured": bool(FALIX_API),
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

# =====================================================
# 💾 SNAPSHOT VŨ TRỤ .QBIE
# =====================================================

def save_snapshot():
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "players": list(PLAYER_STORE.keys()),
        "energy_map": {p: v["energy"] for p, v in PLAYER_STORE.items()},
        "realm_map": {p: REALMS[v["realm_idx"]]["name"] for p, v in PLAYER_STORE.items()},
    }
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 [Fractal] Snapshot saved: {SNAPSHOT_FILE}")

def auto_snapshot_loop():
    while True:
        save_snapshot()
        time.sleep(600)  # 10 phút

@app.post("/snapshot/save")
def snapshot_save_manual():
    save_snapshot()
    return {"ok": True, "file": str(SNAPSHOT_FILE)}

@app.get("/snapshot/load")
def snapshot_load():
    if not SNAPSHOT_FILE.exists():
        raise HTTPException(status_code=404, detail="Snapshot not found")
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# =====================================================
# 🌍 FALIX HEARTBEAT (HỢP LỆ)
# =====================================================

def falix_heartbeat_loop():
    """
    Gửi request nhẹ tới API trạng thái server Falix (do bạn tự cấu hình).
    KHÔNG dùng link 'timer' client.
    Ví dụ: proxy nhỏ của bạn expose /status từ Minecraft server.
    """
    if not FALIX_API:
        print("ℹ️ [Địa Đạo] FALIX_API chưa cấu hình, bỏ qua heartbeat.")
        return

    while True:
        time.sleep(60)  # 60 giây hỏi thăm 1 lần
        try:
            r = requests.get(FALIX_API, timeout=5)
            print(f"🌍 [Địa Đạo] Falix status: {r.status_code}")
        except Exception as e:
            print("⚠️ [Địa Đạo] Falix heartbeat error:", e)

# =====================================================
# 🖥️ DASHBOARD
# =====================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <html>
    <head>
      <title>Celestial Dashboard</title>
      <meta http-equiv="refresh" content="15">
      <style>
        body {{ background-color:#050608; color:#00ffcc; font-family:monospace; text-align:center; }}
        .card {{ background:#101319; padding:20px; margin:20px auto; width:60%; border-radius:10px; }}
        h1 {{ color:#00ffff; }}
        table {{ margin:0 auto; border-collapse:collapse; color:#b8faff; }}
        td,th {{ border:1px solid #1f2533; padding:6px 10px; }}
      </style>
    </head>
    <body>
      <h1>🌌 Celestial QBIES – Thiên Địa Hợp Nhất</h1>
      <div class="card">
        <p>🕒 Thời gian: {now}</p>
        <p>💾 Snapshot: {SNAPSHOT_FILE.name}</p>
        <p>👥 Số người chơi được theo dõi: {len(PLAYER_STORE)}</p>
        <p>🌍 Falix API cấu hình: {"✅" if FALIX_API else "❌"}</p>
      </div>

      <div class="card">
        <h2>👤 Người chơi & Cảnh giới</h2>
        <table>
          <tr><th>Tên</th><th>Cảnh giới</th><th>Linh khí</th></tr>
          { "".join(
              f"<tr><td>{name}</td><td>{REALMS[v['realm_idx']]['name']}</td><td>{round(v['energy'],1)}</td></tr>"
              for name,v in PLAYER_STORE.items()
            ) or "<tr><td colspan='3'>Chưa có ai tu luyện...</td></tr>"
          }
        </table>
      </div>

      <footer>⚡ Celestial QBIES Universe Engine</footer>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# =====================================================
# 🔁 STARTUP HOOK – KHỞI ĐỘNG CÁC VÒNG THIÊN / ĐỊA
# =====================================================

@app.on_event("startup")
def on_startup():
    # Auto snapshot
    threading.Thread(target=auto_snapshot_loop, daemon=True).start()
    # Falix heartbeat (nếu FALIX_API đã cấu hình)
    threading.Thread(target=falix_heartbeat_loop, daemon=True).start()
    print("🌌 [Thiên Đạo] Startup complete – snapshot + heartbeat loops active.")

# =====================================================
# 🏁 ROOT
# =====================================================

@app.get("/")
def root():
    return {
        "msg": "Celestial QBIES Unified Engine Active",
        "time": time.time(),
        "players": len(PLAYER_STORE),
    }