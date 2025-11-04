# =============================================================
# 🌌 Celestial Engine v3.9.1 – Đại Chu Thiên Toàn Đạo Hợp Nhất + Gọi Thức Vĩnh Hằng
# =============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, subprocess, shutil, requests

# --- Import Celestial Modules ---
from coordinator.modules import loader, core_bridge, attributes, karma, willcore, knowledge_map
from coordinator.modules import alchemy, forge, talisman, formation, synchronizer, qbies_kernel

# =============================================================
# ⚙️ KHỞI TẠO HỆ THỐNG
# =============================================================

app = FastAPI(title="Celestial Engine v3.9.1 – Đại Chu Thiên Toàn Đạo Hợp Nhất")

BASE_PATH = os.getcwd()
QCORE_PATH = os.path.join(BASE_PATH, "QCoreBridge")
PLAYER_DATA = os.path.join(BASE_PATH, "coordinator/data/players.qbies")
ENGINE_ID = f"CE-{int(time.time())}"
START_TIME = time.time()

ENGINE_STATUS = {"connected": True, "last_reload": "never", "state": "idle", "ticks": 0}
PLAYER_STATE = {}

os.makedirs(os.path.dirname(PLAYER_DATA), exist_ok=True)

# =============================================================
# 📂 LƯU TRỮ NGƯỜI CHƠI
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
# 🌠 KHỞI TẠO CÁC MODULE
# =============================================================

loader.init(app, config={"base_path": BASE_PATH})

# =============================================================
# 🔄 XÂY DỰNG & TỰ TÁI SINH PLUGIN
# =============================================================

def ensure_plugin_yml():
    try:
        plugin_yml = os.path.join(QCORE_PATH, "plugin.yml")
        if not os.path.exists(plugin_yml):
            os.makedirs(QCORE_PATH, exist_ok=True)
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
            print("[YML FIX] ✅ plugin.yml created")
    except Exception as e:
        print("[YML FIX ERROR]", e)


def build_qcore():
    try:
        ensure_plugin_yml()
        build_dir = os.path.join(QCORE_PATH, "build")
        jar_path = os.path.join(QCORE_PATH, "QCoreBridge.jar")
        if os.path.exists(jar_path): os.remove(jar_path)
        if os.path.exists(build_dir): shutil.rmtree(build_dir)
        os.makedirs(build_dir, exist_ok=True)
        java_files = []
        for r, _, fns in os.walk(os.path.join(QCORE_PATH, "src")):
            for f in fns:
                if f.endswith(".java"): java_files.append(os.path.join(r, f))
        if not java_files:
            raise Exception("Không tìm thấy file .java")
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
        time.sleep(60)
        try:
            r = requests.post("http://localhost:25575/command", data="plugman reload QCoreBridge", timeout=3)
            ENGINE_STATUS["connected"] = (r.status_code == 200)
        except:
            ENGINE_STATUS["connected"] = False
        if not ENGINE_STATUS["connected"]:
            print("[AUTO-RELOAD] ⚠ Lost connection, rebuilding...")
            if build_qcore():
                ENGINE_STATUS["last_reload"] = time.strftime("%H:%M:%S")
                print("[AUTO-RELOAD] ✅ Reload successful")
        ENGINE_STATUS["ticks"] += 1

threading.Thread(target=auto_reload, daemon=True).start()

# =============================================================
# ⚡ API TU LUYỆN & MODULE
# =============================================================

@app.post("/process_event")
async def process_event(req: Request):
    try:
        data = await req.json()
        name = data.get("player", "Unknown")
        gain = float(data.get("energy", 1.0))
        p = PLAYER_STATE.setdefault(name, {"path": None, "energy": 0, "realm": "Phàm Nhân"})

        result = core_bridge.tick(name, gain)
        PLAYER_STATE[name].update(result)
        save_players()
        return result
    except Exception as e:
        return JSONResponse({"error": str(e)})


@app.post("/choose_path")
async def choose_path(req: Request):
    data = await req.json()
    name = data.get("player")
    path = data.get("path")
    res = core_bridge.choose_path(name, path)
    if res.get("ok"):
        PLAYER_STATE[name]["path"] = path
        save_players()
    return res


@app.post("/alchemy")
async def alchemy_route(req: Request):
    data = await req.json()
    recipe = data.get("recipe", {})
    materials = data.get("materials", [])
    res = alchemy.craft_pill(recipe, materials)
    if res.get("ok"):
        karma.add_karma(data.get("player","anon"), +5, "Luyện đan thành công")
    return res


@app.post("/forge")
async def forge_route(req: Request):
    data = await req.json()
    return forge.craft_artifact(data.get("template", {}), data.get("components", []))


@app.post("/talisman")
async def talisman_route(req: Request):
    data = await req.json()
    return talisman.forge_talisman(data.get("formula", {}), data.get("sigils", []))


@app.post("/formation")
async def formation_route(req: Request):
    data = await req.json()
    return formation.create_formation(data.get("owner"), data.get("pattern"), data.get("location"))


@app.post("/knowledge/add")
async def add_knowledge(req: Request):
    data = await req.json()
    return knowledge_map.record_concept(data.get("ns","global"), data.get("concept",""))


@app.post("/qbies/learn")
async def qbies_learn(req: Request):
    data = await req.json()
    return qbies_kernel.learn(data.get("ns","core"), data.get("data",{}))


@app.get("/qbies/summary")
def qbies_summary():
    return qbies_kernel.recall_summary()

# =============================================================
# 🌙 GỌI THỨC – AWAKENING LOOP
# Giữ Render & FalixNodes luôn tỉnh (không auto sleep)
# =============================================================

FALIX_PANEL = "https://panel.falixnodes.net"
RENDER_URL = os.getenv("RENDER_URL", "https://celestial-qbies-engine.onrender.com")

def awaken_cycle():
    while True:
        try:
            # 🪶 1. Gửi nhịp “thức” tới Render
            try:
                requests.get(f"{RENDER_URL}/", timeout=5)
                print("[AWAKEN] Render self-ping ✅")
            except:
                print("[AWAKEN] Render ping failed ⚠")

            # 🔥 2. Ping Falix server qua console hoặc API
            try:
                r = requests.get("http://localhost:25575/command", timeout=3)
                if r.status_code == 200:
                    print("[AWAKEN] Falix local alive ✅")
                else:
                    print("[AWAKEN] Falix ping timeout ⚠ Restarting...")
                    subprocess.run('curl -X POST http://localhost:25575/command -d "restart"', shell=True)
            except Exception as e:
                print("[AWAKEN] FalixNodes unreachable ⚠", e)

            # 🧘 3. Duy trì “Ý chí Thiên Đạo”
            willcore.add_will("ThiênĐạo", +1)
            karma.add_karma("ThiênĐạo", +0.1, "Duy trì thức tỉnh vũ trụ")

            time.sleep(180)  # 3 phút / chu kỳ
        except Exception as e:
            print("[AWAKEN ERROR]", e)
            time.sleep(60)

threading.Thread(target=awaken_cycle, daemon=True).start()

# =============================================================
# 🧩 DASHBOARD
# =============================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - START_TIME)
    html = f"""
    <html><body style='background:black;color:lime;font-family:monospace'>
    <h2>🌌 Celestial Engine v3.9.1 – Đại Chu Thiên Toàn Đạo Hợp Nhất</h2>
    <p>ID: {ENGINE_ID} | Uptime: {uptime}s | Ticks: {ENGINE_STATUS["ticks"]}</p>
    <hr><h3>👤 Người chơi ({len(PLAYER_STATE)})</h3>
    """
    for n, s in PLAYER_STATE.items():
        html += f"<p>{n}: {s.get('path','Chưa nhập')} – {s.get('realm','Phàm Nhân')} ({s.get('energy',0):.1f})</p>"
    html += "<hr><h3>⚙️ Engine</h3>"
    html += f"<p>Connected: {ENGINE_STATUS['connected']}</p><p>Last Reload: {ENGINE_STATUS['last_reload']}</p>"
    html += "</body></html>"
    return HTMLResponse(html)


@app.get("/")
def index():
    return {"engine": "Celestial Engine v3.9.1", "uptime": int(time.time() - START_TIME)}

# =============================================================
# ✅ KẾT THÚC KHỞI ĐỘNG
# =============================================================

print(f"[Celestial Engine v3.9.1] ✅ Hoàn tất khởi động | ID={ENGINE_ID}")