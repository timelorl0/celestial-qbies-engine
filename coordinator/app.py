# =============================================================
# 🌌 Celestial Engine v2.1 – Thiên Đạo Toàn Quyền (Auto-Patch)
# Tự động đồng bộ, vá lỗi, biên dịch và reload plugin Minecraft
# - Thêm: Auto-patch worker (quét PATCH_PATH hoặc PATCH_QUEUE mỗi 60s)
# =============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, base64, subprocess, requests, shutil
from datetime import datetime

app = FastAPI(title="Celestial Engine v2.1 – Thiên Đạo Toàn Quyền (Auto-Patch)")

# ===== Cấu hình (chỉnh theo môi trường của bạn) =====
# Đường dẫn nơi plugin QCoreBridge source nằm (máy chạy Minecraft hoặc volume chia sẻ)
QCORE_PATH = r"C:\QCoreBridge\Thư mục mới\QCoreBridge"   # chỉnh lại khi cần

# Nếu server Minecraft có API reload hoặc endpoint nội bộ để gọi reload, đặt vào đây:
MC_RELOAD_URL = "http://localhost:25575/command?cmd=plugman reload QCoreBridge"  # ví dụ
# Nếu cần dùng curl -> command fallback (Windows hoặc Linux tùy môi trường)
MC_RELOAD_CMD = 'curl -s -X POST "http://localhost:25575/command" -d "plugman reload QCoreBridge"'

ENGINE_ID = f"CE-{int(time.time())}"
START_TIME = time.time()

# Thang cảnh giới (tên, yêu cầu năng lượng, màu)
REALMS = [
    {"name": "Phàm Nhân", "req": 0, "color": "§7"},
    {"name": "Nhập Môn", "req": 50, "color": "§9"},
    {"name": "Trúc Cơ", "req": 200, "color": "§a"},
    {"name": "Ngưng Tuyền", "req": 800, "color": "§e"},
    {"name": "Kim Đan", "req": 2500, "color": "§6"},
    {"name": "Nguyên Anh", "req": 6000, "color": "§d"},
    {"name": "Hóa Thần", "req": 15000, "color": "§5"},
]

# Paths cho coordinator
DATA_DIR = "coordinator/data"
PATCH_PATH = "coordinator/patches"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PATCH_PATH, exist_ok=True)

PLAYER_STATE_FILE = os.path.join(DATA_DIR, "players.qbies")

PLAYER_STATE = {}
PATCH_QUEUE = []        # danh sách đường dẫn file patches đã nhận (full path)
ENGINE_STATUS = {"connected": False, "sync_tick": 0, "last_auto_patch": 0}


# =============================================================
# ⚙️ Hỗ trợ I/O JSON
# =============================================================
def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[SAVE ERROR] {path} -> {e}")

# load saved players on start
PLAYER_STATE = load_json(PLAYER_STATE_FILE, {})


def get_realm_for_energy(e):
    current = REALMS[0]
    for r in REALMS:
        if e >= r["req"]:
            current = r
        else:
            break
    return current


# =============================================================
# 🧘 Thiên Đạo core – nhận sự kiện tick từ plugin
# =============================================================
@app.post("/process_event")
async def process_event(req: Request):
    try:
        ev = await req.json()
    except:
        return JSONResponse({"error": "invalid json"}, status_code=400)

    player = ev.get("player", "Unknown")
    gain = float(ev.get("energy", 1.0))

    p = PLAYER_STATE.setdefault(player, {"energy": 0.0, "realm": "Phàm Nhân", "last": time.time()})
    p["energy"] = p.get("energy", 0.0) + gain
    p["last"] = time.time()

    realm = get_realm_for_energy(p["energy"])
    p["realm"] = realm["name"]

    actions = []
    # check đột phá (nâng cảnh)
    current_index = next((i for i, r in enumerate(REALMS) if r["name"] == realm["name"]), 0)
    next_index = current_index + 1
    if next_index < len(REALMS):
        next_realm = REALMS[next_index]
        if p["energy"] >= next_realm["req"]:
            # thực hiện đột phá
            p["energy"] = 0.0
            p["realm"] = next_realm["name"]
            actions.append({"action": "title", "target": player, "params": {"title": "⚡ ĐỘT PHÁ!", "subtitle": next_realm["name"]}})
            actions.append({"action": "play_sound", "target": player, "params": {"sound": "ENTITY_PLAYER_LEVELUP", "volume": 1.2, "pitch": 0.8}})
            actions.append({"action": "particle", "target": player, "params": {"type": "TOTEM", "count": 60}})

    save_json(PLAYER_STATE_FILE, PLAYER_STATE)
    return {"ok": True, "player": player, "realm": p["realm"], "energy": round(p["energy"], 2), "actions": actions}


# =============================================================
# 🔁 Plugin heartbeat / ping
# =============================================================
@app.post("/plugin/ping")
async def plugin_ping(req: Request):
    try:
        _ = await req.json()
    except:
        pass
    ENGINE_STATUS["connected"] = True
    ENGINE_STATUS["sync_tick"] = time.time()
    return {"ok": True, "msg": "pong"}


# =============================================================
# 🧩 Nhận patch từ UI / render -> lưu vào PATCH_PATH và queue
# =============================================================
@app.post("/plugin/patch")
async def plugin_patch(req: Request):
    """
    Payload:
    {
      "path": "src/qbieslink/QRenderEngine.java",
      "content": "<base64 of file bytes>" 
    }
    """
    try:
        data = await req.json()
    except:
        return JSONResponse({"error": "invalid json"}, status_code=400)

    rel = data.get("path")
    content_b64 = data.get("content")
    if not rel or not content_b64:
        return JSONResponse({"error": "missing path/content"}, status_code=400)

    try:
        raw = base64.b64decode(content_b64)
        out = os.path.join(PATCH_PATH, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as f:
            f.write(raw)
        PATCH_QUEUE.append(out)
        print(f"[PATCH RECEIVED] {out}")
        return {"ok": True, "path": rel}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/plugin/patch_queue")
def plugin_patch_queue():
    return {"queue": PATCH_QUEUE}


# =============================================================
# 🛠️ AUTO-PATCH WORKER
# - Mỗi interval giây: quét PATCH_QUEUE và thư mục PATCH_PATH, áp dụng file vào QCORE_PATH,
#   build plugin (javac + jar) và gửi lệnh reload tới server Minecraft (qua HTTP hoặc command)
# =============================================================
AUTO_PATCH_INTERVAL = 60  # giây

def apply_patch_file(patch_fullpath):
    """
    - Copy patch file into QCORE_PATH (overwrite)
    - Return target path in QCORE_PATH
    """
    try:
        rel = os.path.relpath(patch_fullpath, PATCH_PATH)
        target = os.path.join(QCORE_PATH, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(patch_fullpath, target)
        print(f"[APPLY] Copied {patch_fullpath} -> {target}")
        return target
    except Exception as e:
        print(f"[APPLY ERROR] {patch_fullpath} -> {e}")
        return None

def build_qcore_plugin():
    """
    Build steps:
    - Remove old build & jar
    - Compile java files under src -> build
    - Copy plugin.yml -> build
    - Create jar QCoreBridge.jar in QCORE_PATH
    Note: Implemented cross-platform minimally (works on Windows with provided commands).
    """
    try:
        cwd = QCORE_PATH
        # remove build and jar
        jar_path = os.path.join(cwd, "QCoreBridge.jar")
        build_dir = os.path.join(cwd, "build")
        if os.path.exists(jar_path):
            try: os.remove(jar_path)
            except: pass
        if os.path.exists(build_dir):
            try: shutil.rmtree(build_dir)
            except: pass
        os.makedirs(build_dir, exist_ok=True)

        # find all .java and compile
        java_files = []
        for root, _, files in os.walk(os.path.join(cwd, "src")):
            for f in files:
                if f.endswith(".java"):
                    java_files.append(os.path.join(root, f))
        if not java_files:
            raise RuntimeError("No java sources found under src/")

        # compile (use javac list)
        javac_cmd = ["javac", "--release", "21", "-encoding", "UTF-8", "-cp", "lib/*", "-d", build_dir] + java_files
        print("[BUILD] Running javac...")
        subprocess.run(" ".join(javac_cmd), cwd=cwd, shell=True, check=True)

        # copy plugin.yml
        plugin_yml_src = os.path.join(cwd, "plugin.yml")
        if os.path.exists(plugin_yml_src):
            shutil.copy2(plugin_yml_src, build_dir)
        else:
            print("[BUILD WARN] plugin.yml not found")

        # create jar
        # Use jar command if available
        jar_cmd = f'jar cf "{jar_path}" -C "{build_dir}" .'
        print("[BUILD] Creating jar...")
        subprocess.run(jar_cmd, cwd=cwd, shell=True, check=True)
        print("[BUILD] Success - jar created at", jar_path)
        return True, None
    except subprocess.CalledProcessError as e:
        print("[BUILD ERROR] CalledProcessError:", e)
        return False, str(e)
    except Exception as e:
        print("[BUILD ERROR]:", e)
        return False, str(e)


def reload_minecraft_plugin():
    """
    Try HTTP reload first, then fallback to shell command.
    """
    # Attempt HTTP GET/POST to MC_RELOAD_URL
    try:
        if MC_RELOAD_URL:
            print("[RELOAD] Trying HTTP reload:", MC_RELOAD_URL)
            r = requests.get(MC_RELOAD_URL, timeout=4)
            print("[RELOAD] HTTP status:", r.status_code)
            return True
    except Exception as e:
        print("[RELOAD] HTTP reload failed:", e)

    # fallback command
    try:
        print("[RELOAD] Fallback command:", MC_RELOAD_CMD)
        subprocess.run(MC_RELOAD_CMD, shell=True, check=True)
        return True
    except Exception as e:
        print("[RELOAD] Fallback command failed:", e)
        return False


def auto_patch_worker():
    """
    Worker chính quét PATCH_QUEUE & PATCH_PATH, áp dụng patches, build và reload.
    """
    while True:
        try:
            # 1) collect pending files from PATCH_PATH (if any)
            for root, _, files in os.walk(PATCH_PATH):
                for f in files:
                    full = os.path.join(root, f)
                    if full not in PATCH_QUEUE:
                        PATCH_QUEUE.append(full)

            if PATCH_QUEUE:
                print("[AUTO-PATCH] Found", len(PATCH_QUEUE), "patch(es) -> processing...")
                applied_any = False
                # process snapshot to allow new patches to enqueue
                pending = PATCH_QUEUE.copy()
                PATCH_QUEUE.clear()
                for patch_file in pending:
                    target = apply_patch_file(patch_file)
                    if target:
                        applied_any = True

                if applied_any:
                    ok, err = build_qcore_plugin()
                    if ok:
                        ok2 = reload_minecraft_plugin()
                        ENGINE_STATUS["last_auto_patch"] = int(time.time())
                        print("[AUTO-PATCH] Build+Reload finished:", ok2)
                    else:
                        print("[AUTO-PATCH] Build failed:", err)
            # update heartbeat
            ENGINE_STATUS["sync_tick"] = time.time()
        except Exception as e:
            print("[AUTO-PATCH ERROR]", e)

        time.sleep(AUTO_PATCH_INTERVAL)

# start worker thread
threading.Thread(target=auto_patch_worker, daemon=True).start()


# =============================================================
# 🌠 Dashboard
# =============================================================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - START_TIME)
    html = f"""
    <html><head><title>Celestial Engine v2.1</title></head>
    <body style='background:black;color:lime;font-family:monospace'>
    <h2>🌌 Celestial Engine v2.1 – Thiên Đạo Toàn Quyền</h2>
    <p><b>Engine ID:</b> {ENGINE_ID}</p>
    <p>Connected: {ENGINE_STATUS['connected']}</p>
    <p>Uptime: {uptime}s</p>
    <p>Last Auto-Patch: {datetime.fromtimestamp(ENGINE_STATUS.get('last_auto_patch', 0)).isoformat() if ENGINE_STATUS.get('last_auto_patch') else 'never'}</p>
    <hr>
    <h3>🧬 Player States ({len(PLAYER_STATE)})</h3>
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
# Watchdog (giữ heartbeat)
# =============================================================
def watchdog():
    while True:
        try:
            # nếu đã lâu không ping -> đánh connected false
            if ENGINE_STATUS["connected"] and (time.time() - ENGINE_STATUS["sync_tick"] > 30):
                print("[WATCHDOG] ⚠ Lost ping from plugin")
                ENGINE_STATUS["connected"] = False
        except Exception:
            pass
        time.sleep(5)

threading.Thread(target=watchdog, daemon=True).start()

print(f"[Celestial Engine v2.1] ✅ Khởi động hoàn tất | ID={ENGINE_ID}")