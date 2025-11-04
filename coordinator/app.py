# =============================================================
# 🌌 Celestial Engine v3.9.2 – Đại Chu Thiên Toàn Đạo Hợp Nhất + Gọi Thức Vĩnh Hằng (Ổn Định)
# =============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, subprocess, shutil, requests, sys

# --- Optional import fallback for yaml ---
try:
    import yaml
except ImportError:
    os.system(f"{sys.executable} -m pip install pyyaml")
    import yaml

# --- Import Celestial Modules ---
try:
    from coordinator.modules import loader, core_bridge, attributes, karma, willcore, knowledge_map
    from coordinator.modules import alchemy, forge, talisman, formation, synchronizer, qbies_kernel
except Exception as e:
    print("[MODULE LOAD WARNING]", e)

# =============================================================
# ⚙️ CẤU HÌNH
# =============================================================

app = FastAPI(title="Celestial Engine v3.9.2 – Đại Chu Thiên Toàn Đạo Hợp Nhất")

BASE_PATH = os.getcwd()
QCORE_PATH = os.path.join(BASE_PATH, "QCoreBridge")
PLAYER_DATA = os.path.join(BASE_PATH, "coordinator/data/players.qbies")
ENGINE_ID = f"CE-{int(time.time())}"
START_TIME = time.time()

ENGINE_STATUS = {"connected": True, "last_reload": "never", "state": "idle", "ticks": 0}
PLAYER_STATE = {}
os.makedirs(os.path.dirname(PLAYER_DATA), exist_ok=True)

# =============================================================
# 📜 QUẢN LÝ NGƯỜI CHƠI
# =============================================================

def load_players():
    global PLAYER_STATE
    try:
        if os.path.exists(PLAYER_DATA):
            with open(PLAYER_DATA, "r", encoding="utf-8") as f:
                PLAYER_STATE = json.load(f)
        else:
            PLAYER_STATE = {}
    except Exception as e:
        print("[LOAD ERROR]", e)
        PLAYER_STATE = {}

def save_players():
    try:
        with open(PLAYER_DATA, "w", encoding="utf-8") as f:
            json.dump(PLAYER_STATE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("[SAVE ERROR]", e)

load_players()

# =============================================================
# 🔧 KHỞI TẠO MODULES
# =============================================================

try:
    loader.init(app, config={"base_path": BASE_PATH})
except Exception as e:
    print("[LOADER INIT WARNING]", e)

# =============================================================
# 🔄 AUTO BUILD + RELOAD PLUGIN
# =============================================================

def ensure_plugin_yml():
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
        with open(plugin_yml, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)
        print("[YML FIX] ✅ plugin.yml created")


def build_qcore():
    try:
        ensure_plugin_yml()
        build_dir = os.path.join(QCORE_PATH, "build")
        jar_path = os.path.join(QCORE_PATH, "QCoreBridge.jar")

        if not os.path.exists(os.path.join(QCORE_PATH, "src")):
            print("[BUILD WARN] ⚠ Không có mã nguồn Java để biên dịch (bỏ qua).")
            return True

        if os.path.exists(jar_path): os.remove(jar_path)
        if os.path.exists(build_dir): shutil.rmtree(build_dir)
        os.makedirs(build_dir, exist_ok=True)

        java_files = []
        for r, _, fns in os.walk(os.path.join(QCORE_PATH, "src")):
            for f in fns:
                if f.endswith(".java"): java_files.append(os.path.join(r, f))
        if not java_files:
            print("[BUILD WARN] ⚠ Không tìm thấy file .java (bỏ qua build).")
            return True

        cmd = ["javac", "--release", "21", "-encoding", "UTF-8", "-cp", "lib/*", "-d", build_dir] + java_files
        subprocess.run(" ".join(cmd), cwd=QCORE_PATH, shell=True, check=True)
        shutil.copy2(os.path.join(QCORE_PATH, "plugin.yml"), build_dir)
        subprocess.run(f'jar cf "{jar_path}" -C "{build_dir}" .', cwd=QCORE_PATH, shell=True, check=True)
        print("[BUILD] ✅ QCoreBridge build complete")
        return True
    except Exception as e:
        print("[BUILD ERROR]", e)
        return False


def auto_reload():
    while True:
        time.sleep(90)
        try:
            ENGINE_STATUS["connected"] = True
        except:
            ENGINE_STATUS["connected"] = False

        if not ENGINE_STATUS["connected"]:
            print("[AUTO-RELOAD] ⚠ Lost connection, rebuilding...")
            build_qcore()
            ENGINE_STATUS["last_reload"] = time.strftime("%H:%M:%S")

        ENGINE_STATUS["ticks"] += 1

threading.Thread(target=auto_reload, daemon=True).start()

# =============================================================
# 🌙 GỌI THỨC – AWAKENING LOOP
# =============================================================

RENDER_URL = os.getenv("RENDER_URL", "https://celestial-qbies-engine.onrender.com")
FALIX_PING = "https://panel.falixnodes.net"  # fallback

def awaken_cycle():
    while True:
        try:
            # Ping Render để giữ sống container
            try:
                requests.get(f"{RENDER_URL}/", timeout=5)
                print("[AWAKEN] Render self-ping ✅")
            except Exception as e:
                print("[AWAKEN] Render ping failed ⚠", e)

            # Ping Falix qua HTTP thay vì localhost
            try:
                r = requests.get(FALIX_PING, timeout=5)
                if r.status_code == 200:
                    print("[AWAKEN] Falix heartbeat ✅")
                else:
                    print("[AWAKEN] Falix ping weak ⚠", r.status_code)
            except Exception as e:
                print("[AWAKEN] Falix unreachable ⚠", e)

            # Duy trì “ý chí Thiên Đạo”
            try:
                willcore.add_will("ThiênĐạo", +1)
                karma.add_karma("ThiênĐạo", +0.1, "Duy trì thức tỉnh vũ trụ")
            except Exception as e:
                print("[AWAKEN META] ⚠", e)

            time.sleep(180)
        except Exception as e:
            print("[AWAKEN ERROR]", e)
            time.sleep(60)

threading.Thread(target=awaken_cycle, daemon=True).start()

# =============================================================
# 🧩 API
# =============================================================

@app.get("/")
def index():
    return {"engine": "Celestial Engine v3.9.2", "uptime": int(time.time() - START_TIME)}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - START_TIME)
    html = f"""
    <html><body style='background:black;color:lime;font-family:monospace'>
    <h2>🌌 Celestial Engine v3.9.2 – Gọi Thức Vĩnh Hằng</h2>
    <p>ID: {ENGINE_ID} | Uptime: {uptime}s | Ticks: {ENGINE_STATUS["ticks"]}</p>
    <hr><h3>👤 Người chơi ({len(PLAYER_STATE)})</h3>
    """
    for n, s in PLAYER_STATE.items():
        html += f"<p>{n}: {s.get('path','Chưa nhập')} – {s.get('realm','Phàm Nhân')} ({s.get('energy',0):.1f})</p>"
    html += f"<hr><h3>⚙️ Engine</h3><p>Connected: {ENGINE_STATUS['connected']}</p><p>Last Reload: {ENGINE_STATUS['last_reload']}</p>"
    html += "</body></html>"
    return HTMLResponse(html)

# =============================================================
# ✅ HOÀN TẤT KHỞI ĐỘNG
# =============================================================

print(f"[Celestial Engine v3.9.2] ✅ Khởi động hoàn tất | ID={ENGINE_ID}")