# =============================================================
# 🌌 Celestial Engine v4.3 – Thiên Đạo Tam Hệ + Ngũ Thuật Hợp Nhất
# -------------------------------------------------------------
# ✅ Kết nối Render ↔ FalixNodes
# ✅ Gửi / nhận người chơi thật
# ✅ Auto build & reload plugin QCoreBridge
# ✅ Hệ tu luyện: Tiên – Đạo – Ma – Tự Do
# ✅ Thức 24/24, tự thức dậy khi Render ngủ
# ✅ Thông báo Discord tự động
# =============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, subprocess, shutil, base64, requests, yaml

app = FastAPI(title="Celestial Engine v4.3 – Thiên Đạo Tam Hệ + Ngũ Thuật")

# ====== CẤU HÌNH ======
QCORE_PATH = r"C:\QCoreBridge\Thư mục mới\QCoreBridge"
DATA_DIR = "coordinator/data"
PLAYER_PATH = os.path.join(DATA_DIR, "players.qbies")
PATCH_PATH = "coordinator/patches/"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PATCH_PATH, exist_ok=True)

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1435329688116662304/LJaNXp_Ygm4SjzQid2XBrqS84G2T6ENKm2nFm9AOIifV9PJX67gNTLnF8e4hKWl23x9o"
BASE_URL = "https://celestial-qbies-engine.onrender.com"
ENGINE_ID = f"CE-{int(time.time())}"

PLAYER_STATE = {}
ENGINE_STATUS = {"connected": True, "uptime": 0, "last_reload": "never"}
START_TIME = time.time()

REALMS = [
    "Phàm Nhân", "Nhập Môn", "Luyện Khí", "Trúc Cơ",
    "Kết Đan", "Nguyên Anh", "Hóa Thần", "Luyện Hư",
    "Hợp Thể", "Đại Thừa", "Độ Kiếp"
]
REALM_THRESHOLDS = [0, 50, 200, 800, 3000, 8000, 20000, 50000, 120000, 300000, 1000000]
PATHS = {
    "tutien": "⚡ Tu Tiên",
    "tudao": "☯ Tu Đạo",
    "tuma": "🔥 Tu Ma",
    "tufree": "🌌 Tự Do Tu Hành"
}

# =============================================================
# 🧠 HỖ TRỢ
# =============================================================

def send_discord(msg: str):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=4)
    except Exception as e:
        print("[Discord] ❌", e)

def load_players():
    global PLAYER_STATE
    if os.path.exists(PLAYER_PATH):
        try:
            with open(PLAYER_PATH, "r", encoding="utf-8") as f:
                PLAYER_STATE = json.load(f)
        except:
            PLAYER_STATE = {}

def save_players():
    with open(PLAYER_PATH, "w", encoding="utf-8") as f:
        json.dump(PLAYER_STATE, f, ensure_ascii=False, indent=2)

def ensure_plugin_yml():
    """Tự tạo plugin.yml nếu mất"""
    try:
        plugin_yml = os.path.join(QCORE_PATH, "plugin.yml")
        if not os.path.exists(plugin_yml):
            data = {
                "name": "QCoreBridge",
                "main": "qbieslink.QCoreBridge",
                "version": "1.0.0",
                "api-version": "1.21",
                "commands": {
                    "tuluyen": {"description": "Bắt đầu tu luyện", "usage": "/tuluyen"},
                    "dotpha": {"description": "Đột phá cảnh giới", "usage": "/dotpha"},
                    "tufree": {"description": "Tu tự do hỗn hợp", "usage": "/tufree"},
                }
            }
            with open(plugin_yml, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True)
            print("[YML FIX] ✅ Tạo lại plugin.yml")
    except Exception as e:
        print("[YML FIX ERROR]", e)

# =============================================================
# 🏗️ BUILD & RELOAD
# =============================================================

def build_qcore():
    """Biên dịch lại plugin QCoreBridge"""
    try:
        ensure_plugin_yml()
        cwd = QCORE_PATH
        jar_path = os.path.join(cwd, "QCoreBridge.jar")
        build_dir = os.path.join(cwd, "build")
        if os.path.exists(jar_path): os.remove(jar_path)
        if os.path.exists(build_dir): shutil.rmtree(build_dir)
        os.makedirs(build_dir, exist_ok=True)

        java_files = []
        for r, _, fns in os.walk(os.path.join(cwd, "src")):
            for f in fns:
                if f.endswith(".java"):
                    java_files.append(os.path.join(r, f))
        if not java_files:
            raise Exception("Không tìm thấy file .java")

        cmd = ["javac", "--release", "21", "-encoding", "UTF-8", "-cp", "lib/*", "-d", build_dir] + java_files
        subprocess.run(" ".join(cmd), cwd=cwd, shell=True, check=True)
        shutil.copy2(os.path.join(cwd, "plugin.yml"), build_dir)
        subprocess.run(f'jar cf "{jar_path}" -C "{build_dir}" .', cwd=cwd, shell=True, check=True)

        print("[BUILD] ✅ Build QCoreBridge.jar thành công.")
        send_discord(":white_check_mark: Build QCoreBridge thành công!")
        return True
    except Exception as e:
        print("[BUILD ERROR]", e)
        send_discord(f":x: Build QCoreBridge thất bại: {e}")
        return False

def auto_reload_plugin():
    """Tự reload plugin Falix sau khi build"""
    try:
        resp = requests.post("http://localhost:25575/command", data="plugman reload QCoreBridge", timeout=5)
        if resp.status_code in (200, 204):
            print("[AUTO-RELOAD] 🔁 Reload QCoreBridge thành công.")
            send_discord(":arrows_counterclockwise: Plugin **QCoreBridge** đã reload thành công.")
        else:
            print("[AUTO-RELOAD] ⚠️ Reload trả về:", resp.status_code)
    except Exception as e:
        print("[AUTO-RELOAD] ❌ Lỗi reload:", e)
        send_discord(f":x: Lỗi reload plugin: {e}")

# =============================================================
# 🔄 KEEP ALIVE – NGĂN RENDER/FALIX NGỦ
# =============================================================

def awaken_loop():
    while True:
        try:
            time.sleep(60)
            r1 = requests.get(BASE_URL)
            print("[AWAKEN] Render self-ping ✅", r1.status_code)
            try:
                requests.post("http://localhost:25575/command", data="list", timeout=3)
                print("[AWAKEN] FalixNodes ping ✅")
            except Exception as e:
                print("[AWAKEN Falix] ⚠", e)
        except Exception as e:
            print("[AWAKEN ERROR]", e)

threading.Thread(target=awaken_loop, daemon=True).start()

# =============================================================
# ⚡ API XỬ LÝ SỰ KIỆN NGƯỜI CHƠI
# =============================================================

@app.post("/process_event")
async def process_event(req: Request):
    data = await req.json()
    name = data.get("player", "Unknown")
    gain = float(data.get("energy", 1.0))
    p = PLAYER_STATE.setdefault(name, {"path": "Chưa nhập", "energy": 0.0, "realm": "Phàm Nhân"})

    p["energy"] += gain
    idx = max(i for i, t in enumerate(REALM_THRESHOLDS) if p["energy"] >= t)
    new_realm = REALMS[idx]
    p["realm"] = new_realm
    save_players()

    print(f"[SYNC] 👤 {name}: {p['path']} – {p['realm']} ({p['energy']:.2f})")
    return {"ok": True, "player": name, "realm": new_realm}

@app.post("/choose_path")
async def choose_path(req: Request):
    data = await req.json()
    name = data.get("player")
    path = data.get("path")
    if name and path in PATHS:
        p = PLAYER_STATE.setdefault(name, {"energy": 0.0, "realm": "Phàm Nhân"})
        p["path"] = PATHS[path]
        save_players()
        send_discord(f"🌟 **{name}** đã chọn con đường **{PATHS[path]}**!")
        return {"ok": True, "msg": f"{name} đã chọn {PATHS[path]}"}
    return {"error": "invalid"}

@app.post("/auto_reload")
async def auto_reload_endpoint():
    auto_reload_plugin()
    return {"ok": True, "msg": "Plugin reloaded"}

# =============================================================
# 🌠 DASHBOARD
# =============================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - START_TIME)
    html = f"<html><body style='background:black;color:lime;font-family:monospace'>"
    html += f"<h2>🌌 Celestial Engine v4.3 – Thiên Đạo Tam Hệ + Ngũ Thuật</h2>"
    html += f"<p>ID: {ENGINE_ID} | Uptime: {uptime}s</p><hr>"
    html += f"<h3>👥 Người chơi ({len(PLAYER_STATE)})</h3>"
    for n, s in PLAYER_STATE.items():
        html += f"<p>• {n}: {s.get('path')} – {s.get('realm')} ({s.get('energy'):.2f})</p>"
    html += "</body></html>"
    return HTMLResponse(html)

print(f"[Celestial Engine v4.3] ✅ Hoàn tất khởi động | ID={ENGINE_ID}")
send_discord(f"🪶 **Celestial Engine v4.3** đã khởi động thành công trên Render.")