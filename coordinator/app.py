# =============================================================
# 🌌 Celestial Engine v5.2 – Thiên Đạo Sinh Diệt Chu Kỳ
# Quản lý Tam Đạo + Tu Tự Do + Ngũ Nghệ + Phản Phệ & Tàn Phiến
# =============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, subprocess, shutil, base64, requests

app = FastAPI(title="Celestial Engine v5.2 – Thiên Đạo Sinh Diệt Chu Kỳ")

# ===== ĐƯỜNG DẪN =====
QCORE_PATH = r"C:\QCoreBridge\Thư mục mới\QCoreBridge"
DATA_DIR = "coordinator/data"
PLAYER_PATH = os.path.join(DATA_DIR, "players.qbies")
PATCH_PATH = "coordinator/patches/"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PATCH_PATH, exist_ok=True)

BASE_URL = "https://celestial-qbies-engine.onrender.com"
ENGINE_ID = f"CE-{int(time.time())}"
START_TIME = time.time()

PLAYER_STATE = {}
ENGINE_STATUS = {
    "connected": True,
    "sync_tick": 0,
    "last_auto_reload": "never",
    "last_auto_status": "idle"
}

# =============================================================
# ⚙️ CẤU TRÚC CẢNH GIỚI
# =============================================================
REALMS = [
    "Phàm Nhân", "Nhập Môn", "Luyện Khí", "Trúc Cơ", "Kết Đan",
    "Nguyên Anh", "Hóa Thần", "Luyện Hư", "Hợp Thể", "Đại Thừa", "Độ Kiếp"
]
REALM_THRESHOLDS = [0, 50, 200, 800, 3000, 8000, 20000, 50000, 120000, 300000, 1000000]
PATHS = {
    "tutien": {"name": "Tu Tiên"},
    "tudao": {"name": "Tu Đạo"},
    "tuma": {"name": "Tu Ma"},
    "tuluyen": {"name": "Tu Tự Do"}
}

# =============================================================
# 📜 HÀM HỖ TRỢ
# =============================================================

def load_players():
    global PLAYER_STATE
    try:
        if os.path.exists(PLAYER_PATH):
            with open(PLAYER_PATH, "r", encoding="utf-8") as f:
                PLAYER_STATE = json.load(f)
        else:
            PLAYER_STATE = {}
    except:
        PLAYER_STATE = {}

def save_players():
    try:
        with open(PLAYER_PATH, "w", encoding="utf-8") as f:
            json.dump(PLAYER_STATE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("[SAVE ERROR]", e)

load_players()

# =============================================================
# 🧬 TỰ SINH - TỰ DIỆT - TỰ HÓA (Tàn Phiến)
# =============================================================

@app.post("/create_fragment")
async def create_fragment(req: Request):
    data = await req.json()
    name = data.get("player")
    reason = data.get("reason", "unknown")
    frag_file = os.path.join(DATA_DIR, f"fragment_{name}.json")
    with open(frag_file, "w", encoding="utf-8") as f:
        json.dump({"player": name, "reason": reason, "time": time.time()}, f, ensure_ascii=False, indent=2)
    print(f"[FRAGMENT] ✴️ Tạo tàn phiến cho {name} do {reason}")
    return {"ok": True, "message": f"Tàn phiến {name} sinh ra do {reason}"}

def fragment_cycle():
    while True:
        try:
            now = time.time()
            for file in os.listdir(DATA_DIR):
                if file.startswith("fragment_") and file.endswith(".json"):
                    path = os.path.join(DATA_DIR, file)
                    with open(path, "r", encoding="utf-8") as f:
                        frag = json.load(f)
                    age = now - frag.get("time", now)
                    if age > 86400:  # Sau 24 giờ
                        if age < 90000 and os.path.exists(path):
                            print(f"[FRAGMENT] ☯️ {frag['player']} tàn phiến hòa tan linh khí.")
                            os.remove(path)
        except Exception as e:
            print("[FRAGMENT ERROR]", e)
        time.sleep(600)  # Kiểm tra mỗi 10 phút

threading.Thread(target=fragment_cycle, daemon=True).start()

# =============================================================
# ⚡ XỬ LÝ TU LUYỆN
# =============================================================

@app.post("/process_event")
async def process_event(req: Request):
    try:
        data = await req.json()
        name = data.get("player", "Unknown")
        energy_gain = float(data.get("energy", 1.0))
        p = PLAYER_STATE.setdefault(name, {"path": "tuluyen", "energy": 0, "realm": "Phàm Nhân"})
        p["energy"] += energy_gain

        idx = max(i for i, t in enumerate(REALM_THRESHOLDS) if p["energy"] >= t)
        new_realm = REALMS[idx]
        p["realm"] = new_realm
        save_players()

        if idx + 1 < len(REALM_THRESHOLDS) and p["energy"] >= REALM_THRESHOLDS[idx + 1]:
            p["energy"] = 0.0
            p["realm"] = REALMS[idx + 1]
            print(f"[ASCEND] ⚡ {name} đột phá → {p['realm']}")
            save_players()

        return {"ok": True, "player": name, "realm": p["realm"], "energy": p["energy"]}
    except Exception as e:
        return {"error": str(e)}

# =============================================================
# 🌠 ĐIỀU KHIỂN HỆ THỐNG & DASHBOARD
# =============================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - START_TIME)
    html = f"<html><body style='background:black;color:lime;font-family:monospace'>"
    html += f"<h2>🌌 Celestial Engine v5.2 – Thiên Đạo Sinh Diệt</h2>"
    html += f"<p>ID: {ENGINE_ID} | Uptime: {uptime}s</p><hr>"
    for n, s in PLAYER_STATE.items():
        html += f"<p>👤 {n}: {s.get('path')} – {s.get('realm')} ({s.get('energy', 0):.2f})</p>"
    html += "</body></html>"
    return HTMLResponse(html)

# =============================================================
# 🔁 TỰ KHỞI ĐỘNG NỀN & GIỮ RENDER HOẠT ĐỘNG
# =============================================================

def awaken_cycle():
    while True:
        try:
            requests.get(BASE_URL, timeout=5)
            print("[AWAKEN] 🌙 Render Engine vẫn đang hoạt động.")
        except:
            print("[AWAKEN] ⚠️ Ping thất bại – vẫn giữ tiến trình nền.")
        time.sleep(60)

threading.Thread(target=awaken_cycle, daemon=True).start()

print(f"[Celestial Engine v5.2] ✅ Khởi động hoàn tất | ID={ENGINE_ID}")