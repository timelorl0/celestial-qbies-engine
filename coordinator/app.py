# =============================================================
# 🌌 Celestial Engine v4.0.1 – Watcher of Heaven
# Thiên Đạo Gọi Thức + Discord Webhook Cảnh Báo Node
# =============================================================

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os, json, time, threading, subprocess, shutil, requests, sys

# ---- Thư viện phụ trợ ----
try:
    import yaml
except ImportError:
    os.system(f"{sys.executable} -m pip install pyyaml")
    import yaml

# =============================================================
# ⚙️ CẤU HÌNH
# =============================================================

app = FastAPI(title="Celestial Engine v4.0.1 – Watcher of Heaven")

BASE_PATH = os.getcwd()
QCORE_PATH = os.path.join(BASE_PATH, "QCoreBridge")
PLAYER_DATA = os.path.join(BASE_PATH, "coordinator/data/players.qbies")
ENGINE_ID = f"CE-{int(time.time())}"
START_TIME = time.time()

ENGINE_STATUS = {"connected": True, "last_reload": "never", "state": "idle", "ticks": 0}
PLAYER_STATE = {}
os.makedirs(os.path.dirname(PLAYER_DATA), exist_ok=True)

# 🌐 Webhook Discord thật của bạn
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1435326612110442678/CU5xNQZP80scsiO1sY6XxH3md7nkttSqm26wm1pjO_eghfnOI_guJyH4VdejEqaVOyZw"

RENDER_URL = os.getenv("RENDER_URL", "https://celestial-qbies-engine.onrender.com")
FALIX_PING = "https://panel.falixnodes.net"

# =============================================================
# 📡 GỬI THÔNG BÁO DISCORD
# =============================================================

def send_discord_alert(title: str, message: str, color: int = 0x00FFAA, icon: str = "🌌"):
    """Gửi thông báo lên Discord"""
    try:
        data = {
            "username": "Celestial Watcher",
            "embeds": [{
                "title": f"{icon} {title}",
                "description": message,
                "color": color,
                "footer": {"text": f"Thiên Đạo • {time.strftime('%H:%M:%S')}"}
            }]
        }
        requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
    except Exception as e:
        print("[DISCORD WARN]", e)

# =============================================================
# 🧬 QUẢN LÝ NGƯỜI CHƠI
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
        if os.path.exists(jar_path): os.remove(jar_path)
        if os.path.exists(build_dir): shutil.rmtree(build_dir)
        os.makedirs(build_dir, exist_ok=True)
        print("[BUILD] ⚙️ Build QCore skipped (no Java on Render).")
        return True
    except Exception as e:
        print("[BUILD ERROR]", e)
        return False


def auto_reload():
    while True:
        time.sleep(90)
        try:
            requests.get(RENDER_URL, timeout=4)
            ENGINE_STATUS["connected"] = True
        except:
            ENGINE_STATUS["connected"] = False

        if not ENGINE_STATUS["connected"]:
            print("[AUTO-RELOAD] ⚠ Lost connection, rebuilding...")
            build_qcore()
            ENGINE_STATUS["last_reload"] = time.strftime("%H:%M:%S")
            send_discord_alert("Render tái sinh ⚙️", "Render node vừa được Thiên Đạo khởi động lại.", 0xFFFF00, "🌀")

        ENGINE_STATUS["ticks"] += 1

threading.Thread(target=auto_reload, daemon=True).start()

# =============================================================
# 🌙 GỌI THỨC – WATCHER LOOP
# =============================================================

def awaken_cycle():
    last_render_alive = True
    last_falix_alive = True

    while True:
        try:
            # --- Ping Render ---
            try:
                requests.get(f"{RENDER_URL}/", timeout=5)
                if not last_render_alive:
                    send_discord_alert("Render tỉnh lại 🌈", "Render node đã hồi sinh và đang hoạt động.", 0x00FFAA)
                last_render_alive = True
                print("[AWAKEN] Render self-ping ✅")
            except Exception as e:
                print("[AWAKEN] Render unreachable ⚠", e)
                if last_render_alive:
                    send_discord_alert("Render rơi vào ngủ sâu 💤", "Render node mất phản hồi ping.", 0xFF8800)
                last_render_alive = False

            # --- Ping Falix ---
            try:
                r = requests.get(FALIX_PING, timeout=5)
                if r.status_code == 200:
                    if not last_falix_alive:
                        send_discord_alert("Falix hồi sinh 🔥", "FalixNodes đã tỉnh giấc và đang chạy ổn định.", 0x00FFAA)
                    last_falix_alive = True
                    print("[AWAKEN] Falix heartbeat ✅")
                else:
                    print("[AWAKEN] Falix weak ⚠")
                    if last_falix_alive:
                        send_discord_alert("Falix yếu sinh khí ⚠", f"HTTP {r.status_code} – phản hồi không ổn định.", 0xFFAA00)
                    last_falix_alive = False
            except Exception as e:
                print("[AWAKEN] Falix unreachable ⚠", e)
                if last_falix_alive:
                    send_discord_alert("Falix hôn mê 💤", "FalixNodes mất kết nối, Thiên Đạo đang quan sát.", 0xFF0000)
                last_falix_alive = False

            ENGINE_STATUS["ticks"] += 1
            time.sleep(180)

        except Exception as e:
            print("[AWAKEN ERROR]", e)
            time.sleep(60)

threading.Thread(target=awaken_cycle, daemon=True).start()

# =============================================================
# 🧩 DASHBOARD
# =============================================================

@app.get("/")
def index():
    return {"engine": "Celestial Engine v4.0.1 – Watcher of Heaven", "uptime": int(time.time() - START_TIME)}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - START_TIME)
    html = f"""
    <html><body style='background:black;color:lime;font-family:monospace'>
    <h2>🌌 Celestial Engine v4.0.1 – Watcher of Heaven</h2>
    <p>ID: {ENGINE_ID} | Uptime: {uptime}s | Ticks: {ENGINE_STATUS["ticks"]}</p>
    <hr><h3>👤 Người chơi ({len(PLAYER_STATE)})</h3>
    """
    for n, s in PLAYER_STATE.items():
        html += f"<p>{n}: {s.get('path','Chưa nhập')} – {s.get('realm','Phàm Nhân')} ({s.get('energy',0):.1f})</p>"
    html += f"<hr><h3>⚙️ Engine</h3><p>Connected: {ENGINE_STATUS['connected']}</p><p>Last Reload: {ENGINE_STATUS['last_reload']}</p>"
    html += "</body></html>"
    return HTMLResponse(html)

print(f"[Celestial Engine v4.0.1] ✅ Khởi động hoàn tất | ID={ENGINE_ID}")
send_discord_alert("Thiên Đạo thức giấc ✨", f"Celestial Engine v4.0.1 đã khởi động | ID={ENGINE_ID}", 0x00FFFF)