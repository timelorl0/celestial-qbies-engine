# =============================================================
# 🌌 Celestial Engine v3.0 – Thiên Đạo Tam Hệ Toàn Quyền
# Tự động vá lỗi, biên dịch plugin, và quản lý tu luyện (Tu Tiên – Tu Đạo – Tu Ma)
# =============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, subprocess, shutil, base64, requests

app = FastAPI(title="Celestial Engine v3.0 – Thiên Đạo Tam Hệ Toàn Quyền")

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

# ===== BỘ NHỚ HỆ THỐNG =====
PLAYER_STATE = {}
ENGINE_STATUS = {
    "connected": True,
    "sync_tick": 0,
    "last_auto_reload": "never",
    "last_auto_status": "idle"
}


# =============================================================
# ⚙️ CẤU HÌNH HỆ CẢNH GIỚI TAM ĐẠO
# =============================================================

REALMS = [
    "Phàm Nhân", "Nhập Môn", "Luyện Khí", "Trúc Cơ",
    "Kết Đan", "Nguyên Anh", "Hóa Thần", "Luyện Hư",
    "Hợp Thể", "Đại Thừa", "Độ Kiếp"
]

REALM_THRESHOLDS = [0, 50, 200, 800, 3000, 8000, 20000, 50000, 120000, 300000, 1000000]

PATHS = {
    "tutien": {"name": "Tu Tiên", "energy_key": "energy"},
    "tudao": {"name": "Tu Đạo", "energy_key": "insight"},
    "tuma": {"name": "Tu Ma", "energy_key": "malust"}
}


# =============================================================
# 📜 HÀM HỖ TRỢ
# =============================================================

def load_players():
    global PLAYER_STATE
    if os.path.exists(PLAYER_PATH):
        try:
            with open(PLAYER_PATH, "r", encoding="utf-8") as f:
                PLAYER_STATE = json.load(f)
        except:
            PLAYER_STATE = {}

def save_players():
    try:
        with open(PLAYER_PATH, "w", encoding="utf-8") as f:
            json.dump(PLAYER_STATE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("[SAVE ERROR]", e)

load_players()

def ensure_plugin_yml():
    try:
        plugin_yml = os.path.join(QCORE_PATH, "plugin.yml")
        if not os.path.exists(plugin_yml):
            data = {
                "name": "QCoreBridge",
                "main": "qbieslink.QCoreBridge",
                "version": "1.0.0",
                "api-version": "1.21",
                "commands": {
                    "tuluyen": {"description": "Bắt đầu tu luyện linh khí", "usage": "/tuluyen"},
                    "dotpha": {"description": "Đột phá cảnh giới", "usage": "/dotpha"}
                }
            }
            import yaml
            with open(plugin_yml, "w", encoding="utf-8") as f:
                yaml.dump(data, f, sort_keys=False, allow_unicode=True)
            print("[YML FIX] ✅ Đã tạo plugin.yml")
    except Exception as e:
        print("[YML FIX] ❌", e)


def build_qcore():
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
                if f.endswith(".java"): java_files.append(os.path.join(r, f))
        if not java_files:
            raise Exception("Không tìm thấy file .java")

        cmd = ["javac", "--release", "21", "-encoding", "UTF-8", "-cp", "lib/*", "-d", build_dir] + java_files
        subprocess.run(" ".join(cmd), cwd=cwd, shell=True, check=True)

        shutil.copy2(os.path.join(cwd, "plugin.yml"), build_dir)
        subprocess.run(f'jar cf "{jar_path}" -C "{build_dir}" .', cwd=cwd, shell=True, check=True)
        print("[BUILD] ✅ QCoreBridge build thành công!")
        return True
    except Exception as e:
        print("[BUILD ERROR]", e)
        return False


def auto_reload():
    while True:
        time.sleep(45)
        try:
            resp = requests.post(BASE_URL + "/plugin/ping", json={"ping": True}, timeout=4)
            if resp.status_code == 200:
                ENGINE_STATUS["connected"] = True
                continue
        except:
            ENGINE_STATUS["connected"] = False

        if not ENGINE_STATUS["connected"]:
            print("[AUTO-RELOAD] ⚠ Mất kết nối, tiến hành vá & reload plugin...")
            if build_qcore():
                try:
                    subprocess.run('curl -X POST http://localhost:25575/command -d "plugman reload QCoreBridge"', shell=True)
                    ENGINE_STATUS["last_auto_status"] = "success"
                    ENGINE_STATUS["last_auto_reload"] = time.strftime("%H:%M:%S")
                    print("[AUTO-RELOAD] ✅ Reload thành công.")
                except Exception as e:
                    ENGINE_STATUS["last_auto_status"] = f"reload_failed: {e}"
                    print("[AUTO-RELOAD] ❌ Lỗi reload:", e)

threading.Thread(target=auto_reload, daemon=True).start()


# =============================================================
# ⚡ HỆ TU LUYỆN
# =============================================================

@app.post("/process_event")
async def process_event(req: Request):
    try:
        data = await req.json()
        name = data.get("player", "Unknown")
        p = PLAYER_STATE.setdefault(name, {"path": None, "energy": 0, "realm": "Phàm Nhân"})

        # Nếu chưa chọn hệ tu luyện
        if not p.get("path"):
            return {
                "choose_path": True,
                "options": [
                    {"id": "tutien", "name": "⚡ Tu Tiên"},
                    {"id": "tudao", "name": "☯ Tu Đạo"},
                    {"id": "tuma", "name": "🔥 Tu Ma"}
                ]
            }

        gain = float(data.get("energy", 1.0))
        p["energy"] += gain
        thresholds = REALM_THRESHOLDS
        idx = max(i for i, t in enumerate(thresholds) if p["energy"] >= t)
        new_realm = REALMS[idx]
        p["realm"] = new_realm
        save_players()

        actions = [
            {"action": "set_ui", "target": name, "params": {"path": p['path'], "realm": new_realm, "energy": round(p['energy'], 2)}}
        ]

        if idx + 1 < len(thresholds) and p["energy"] >= thresholds[idx + 1]:
            actions += [
                {"action": "title", "target": name, "params": {"title": "⚡ ĐỘT PHÁ!", "subtitle": REALMS[idx + 1]}},
                {"action": "particle", "target": name, "params": {"type": "TOTEM", "count": 60}},
                {"action": "sound", "target": name, "params": {"sound": "ENTITY_PLAYER_LEVELUP", "volume": 1.3}}
            ]
            p["energy"] = 0.0
            p["realm"] = REALMS[idx + 1]
            save_players()

        return {"ok": True, "player": name, "realm": new_realm, "actions": actions}

    except Exception as e:
        return {"error": str(e)}


@app.post("/choose_path")
async def choose_path(req: Request):
    data = await req.json()
    name = data.get("player")
    path = data.get("path")
    if name and path in PATHS:
        p = PLAYER_STATE.setdefault(name, {"energy": 0.0, "realm": "Phàm Nhân"})
        p["path"] = path
        save_players()
        return {
            "ok": True,
            "message": f"{name} đã nhập {PATHS[path]['name']}!",
            "actions": [
                {"action": "title", "target": name, "params": {"title": PATHS[path]["name"], "subtitle": "Bắt đầu tu luyện"}},
                {"action": "particle", "target": name, "params": {"type": "ENCHANT", "count": 50}}
            ]
        }
    return {"error": "invalid"}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - START_TIME)
    html = f"""
    <html><body style='background:black;color:lime;font-family:monospace'>
    <h2>🌌 Celestial Engine v3.0 – Thiên Đạo Tam Hệ Toàn Quyền</h2>
    <p>Engine ID: {ENGINE_ID} | Uptime: {uptime}s</p>
    <hr><h3>Người chơi ({len(PLAYER_STATE)})</h3>
    """
    for n, s in PLAYER_STATE.items():
        html += f"<p>👤 {n}: {s.get('path','Chưa nhập')} – {s.get('realm','Phàm Nhân')} ({s.get('energy',0):.2f})</p>"
    html += "</body></html>"
    return HTMLResponse(html)


print(f"[Celestial Engine v3.0] ✅ Khởi động hoàn tất | ID={ENGINE_ID}")