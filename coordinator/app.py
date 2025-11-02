# =============================================================
# 🌌 Celestial Engine v2.0 – Thiên Đạo Toàn Quyền
# Tự động đồng bộ, vá lỗi và quản lý cảnh giới Minecraft
# =============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, math, requests, base64
from datetime import datetime

app = FastAPI(title="Celestial Engine v2.0 – Thiên Đạo Toàn Quyền")

# ===== ĐƯỜNG DẪN DỮ LIỆU =====
DATA_PATH = "coordinator/data/memory.qbies"
PLAYER_PATH = "coordinator/data/players.qbies"
PATCH_PATH = "coordinator/patches/"
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
os.makedirs(PATCH_PATH, exist_ok=True)

BASE_URL = "https://celestial-qbies-engine.onrender.com"
ENGINE_ID = f"CE-{int(time.time())}"
START_TIME = time.time()
REALMS = [
    {"name": "Phàm Nhân", "req": 0, "color": "§7"},
    {"name": "Nhập Môn", "req": 50, "color": "§9"},
    {"name": "Trúc Cơ", "req": 200, "color": "§a"},
    {"name": "Ngưng Tuyền", "req": 800, "color": "§e"},
    {"name": "Kim Đan", "req": 2500, "color": "§6"},
    {"name": "Nguyên Anh", "req": 6000, "color": "§d"},
    {"name": "Hóa Thần", "req": 15000, "color": "§5"},
]

# ===== BỘ NHỚ CẢNH GIỚI & NĂNG LƯỢNG =====
PLAYER_STATE = {}
PATCH_QUEUE = []
ENGINE_STATUS = {"connected": True, "entropy": 0.0, "sync_tick": 0}


# ===== HÀM HỖ TRỢ =====
def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except:
        pass
    return default


def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[SAVE ERROR] {path} → {e}")


def get_realm_for_energy(e):
    current = REALMS[0]
    for r in REALMS:
        if e >= r["req"]:
            current = r
        else:
            break
    return current


# =============================================================
# 🧘 THIÊN ĐẠO – CỐT LÕI TU LUYỆN
# =============================================================

@app.post("/process_event")
async def process_event(req: Request):
    try:
        ev = await req.json()
    except:
        return JSONResponse({"error": "invalid json"}, status_code=400)

    player = ev.get("player", "Unknown")
    p = PLAYER_STATE.setdefault(player, {"energy": 0.0, "realm": "Phàm Nhân", "last": time.time()})

    if ev.get("type") == "tick":
        gain = float(ev.get("energy", 1.0))
        p["energy"] += gain
        p["last"] = time.time()

    # Xác định cảnh giới hiện tại
    realm = get_realm_for_energy(p["energy"])
    p["realm"] = realm["name"]

    # Tính năng ĐỘT PHÁ
    actions = []
    if p["energy"] >= realm["req"]:
        next_index = next((i for i, r in enumerate(REALMS) if r["name"] == realm["name"]), 0) + 1
        if next_index < len(REALMS):
            next_realm = REALMS[next_index]
            if p["energy"] >= next_realm["req"]:
                p["energy"] = 0.0
                p["realm"] = next_realm["name"]
                actions += [
                    {"action": "title", "target": player, "params": {"title": "⚡ ĐỘT PHÁ!", "subtitle": next_realm["name"]}},
                    {"action": "play_sound", "target": player, "params": {"sound": "ENTITY_PLAYER_LEVELUP", "volume": 1.2, "pitch": 0.6}},
                    {"action": "particle", "target": player, "params": {"type": "TOTEM", "count": 60, "offset": [0, 1.5, 0]}}
                ]

    save_json(PLAYER_PATH, PLAYER_STATE)
    return JSONResponse({"ok": True, "player": player, "realm": p["realm"], "energy": round(p["energy"], 2), "actions": actions})


# =============================================================
# 🧩 QUẢN LÝ PLUGIN MINECRAFT
# =============================================================

@app.post("/plugin/ping")
async def plugin_ping(req: Request):
    data = await req.json()
    ENGINE_STATUS["connected"] = True
    ENGINE_STATUS["sync_tick"] = time.time()
    return {"ok": True, "msg": "Ping received", "time": ENGINE_STATUS["sync_tick"]}


@app.post("/plugin/patch")
async def plugin_patch(req: Request):
    """Nhận patch từ Render để sửa file trong plugin"""
    data = await req.json()
    rel_path = data.get("path")
    content = data.get("content")

    if not rel_path or not content:
        return JSONResponse({"error": "invalid patch"}, status_code=400)

    try:
        raw = base64.b64decode(content)
        out_path = os.path.join(PATCH_PATH, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(raw)
        print(f"[PATCH] ✅ Saved patch to {out_path}")
        PATCH_QUEUE.append(out_path)
        return {"ok": True, "path": rel_path}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/plugin/patch_queue")
def plugin_patch_queue():
    return {"queue": PATCH_QUEUE}


@app.get("/plugin/reload")
def plugin_reload():
    """Lệnh reload plugin QCoreBridge bên Minecraft"""
    try:
        requests.post(BASE_URL + "/plugin/reload", timeout=3)
        return {"ok": True, "msg": "Reload requested"}
    except:
        return {"ok": False, "msg": "Minecraft unreachable"}


# =============================================================
# 🌠 DASHBOARD GIÁM SÁT THIÊN ĐẠO
# =============================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - START_TIME)
    players = len(PLAYER_STATE)
    html = f"""
    <html><head><title>Celestial Engine v2.0</title></head>
    <body style='background:black;color:lime;font-family:monospace'>
    <h2>🌌 Celestial Engine v2.0 – Thiên Đạo Toàn Quyền</h2>
    <p><b>Engine ID:</b> {ENGINE_ID}</p>
    <p>Connected: {ENGINE_STATUS['connected']}</p>
    <p>Uptime: {uptime}s</p>
    <hr>
    <h3>🧬 Player States ({players})</h3>
    """
    for name, st in PLAYER_STATE.items():
        html += f"<p>👤 <b>{name}</b> → {st['realm']} ({st['energy']:.2f})</p>"
    html += """
    <hr><p><a href='/plugin/patch_queue' style='color:cyan'>→ Patch Queue</a></p>
    <script>setTimeout(()=>location.reload(),5000)</script>
    </body></html>
    """
    return HTMLResponse(html)


# =============================================================
# 🔄 LUỒNG GIÁM SÁT & KHÔI PHỤC
# =============================================================

def watchdog():
    while True:
        time.sleep(10)
        if ENGINE_STATUS["connected"] and (time.time() - ENGINE_STATUS["sync_tick"] > 30):
            print("[WATCHDOG] ⚠ Mất kết nối Minecraft → cố gắng đồng bộ lại...")
            ENGINE_STATUS["connected"] = False


threading.Thread(target=watchdog, daemon=True).start()

print(f"[Celestial Engine v2.0] ✅ Khởi động hoàn tất | ID={ENGINE_ID}")