# =============================================================
# 🌌 Celestial Engine v2.3 – Thiên Đạo Toàn Quyền
# Tự động đồng bộ, vá lỗi và quản lý cảnh giới Minecraft
# =============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, subprocess, base64, shutil, requests

app = FastAPI(title="Celestial Engine v2.3 – Thiên Đạo Toàn Quyền")

# ===== ĐƯỜNG DẪN =====
QCORE_PATH = r"C:\QCoreBridge\Thư mục mới\QCoreBridge"
DATA_PATH = "coordinator/data/memory.qbies"
PLAYER_PATH = "coordinator/data/players.qbies"
PATCH_PATH = "coordinator/patches/"
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
os.makedirs(PATCH_PATH, exist_ok=True)

BASE_URL = "https://celestial-qbies-engine.onrender.com"
ENGINE_ID = f"CE-{int(time.time())}"
START_TIME = time.time()

# ===== BỘ NHỚ HỆ THỐNG =====
PLAYER_STATE = {}
PATCH_QUEUE = []
ENGINE_STATUS = {
    "connected": True,
    "entropy": 0.0,
    "sync_tick": 0,
    "last_auto_reload": "never",
    "last_auto_status": "idle"
}


# =============================================================
# 🧩 HÀM HỖ TRỢ CƠ BẢN
# =============================================================

def ensure_plugin_yml():
    """Kiểm tra & vá plugin.yml"""
    try:
        import yaml
        plugin_yml_path = os.path.join(QCORE_PATH, "plugin.yml")
        required = {
            "name": "QCoreBridge",
            "main": "qbieslink.QCoreBridge",
            "version": "1.0.0",
            "api-version": "1.21",
            "author": "Celestial Engine",
            "description": "Liên kết Thiên Đạo và thế giới Minecraft - QCoreBridge",
            "commands": {
                "tuluyen": {
                    "description": "Bắt đầu tu luyện linh khí",
                    "usage": "/tuluyen"
                },
                "dotpha": {
                    "description": "Cố gắng đột phá lên cảnh giới cao hơn",
                    "usage": "/dotpha"
                }
            }
        }

        if not os.path.exists(plugin_yml_path):
            with open(plugin_yml_path, "w", encoding="utf-8") as f:
                yaml.dump(required, f, sort_keys=False, allow_unicode=True)
            print("[YML FIX] ⚙️ plugin.yml chưa tồn tại → tạo mới.")
            return True

        with open(plugin_yml_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "name:" not in content or "main:" not in content:
            with open(plugin_yml_path, "w", encoding="utf-8") as f:
                yaml.dump(required, f, sort_keys=False, allow_unicode=True)
            print("[YML FIX] ⚠️ plugin.yml bị lỗi → vá lại.")
            return True
        return False
    except Exception as e:
        print("[YML FIX] ❌ Lỗi khi kiểm tra plugin.yml:", e)
        return False


def build_qcore_plugin():
    """Biên dịch lại toàn bộ plugin"""
    try:
        ensure_plugin_yml()

        cwd = QCORE_PATH
        jar_path = os.path.join(cwd, "QCoreBridge.jar")
        build_dir = os.path.join(cwd, "build")
        if os.path.exists(jar_path):
            try: os.remove(jar_path)
            except: pass
        if os.path.exists(build_dir):
            try: shutil.rmtree(build_dir)
            except: pass
        os.makedirs(build_dir, exist_ok=True)

        # Tìm file Java
        java_files = []
        for root, _, files in os.walk(os.path.join(cwd, "src")):
            for f in files:
                if f.endswith(".java"):
                    java_files.append(os.path.join(root, f))
        if not java_files:
            raise RuntimeError("Không tìm thấy file .java trong src/")

        javac_cmd = ["javac", "--release", "21", "-encoding", "UTF-8", "-cp", "lib/*", "-d", build_dir] + java_files
        subprocess.run(" ".join(javac_cmd), cwd=cwd, shell=True, check=True)

        shutil.copy2(os.path.join(cwd, "plugin.yml"), build_dir)
        subprocess.run(f'jar cf "{jar_path}" -C "{build_dir}" .', cwd=cwd, shell=True, check=True)

        print("[BUILD] ✅ QCoreBridge.jar đã được build thành công!")
        return True, None
    except subprocess.CalledProcessError as e:
        print("[BUILD ERROR] ❌ Lỗi biên dịch:", e)
        return False, str(e)
    except Exception as e:
        print("[BUILD ERROR] ❌", e)
        return False, str(e)


# =============================================================
# ♻️ AUTO-RELOAD PLUGIN
# =============================================================

def auto_reload_worker():
    while True:
        time.sleep(30)
        try:
            resp = requests.post(BASE_URL + "/plugin/ping", json={"test": True}, timeout=5)
            if resp.status_code == 200:
                ENGINE_STATUS["connected"] = True
                ENGINE_STATUS["sync_tick"] = time.time()
                continue
        except Exception as e:
            print(f"[AUTO-RELOAD] ⚠ Mất kết nối: {e}")
            ENGINE_STATUS["connected"] = False

        # Nếu mất kết nối hoặc plugin disable
        if not ENGINE_STATUS["connected"]:
            print("[AUTO-RELOAD] ⚙ Phát hiện QCoreBridge bị disable → tiến hành vá & reload.")
            ENGINE_STATUS["last_auto_reload"] = time.strftime("%H:%M:%S")
            ENGINE_STATUS["last_auto_status"] = "running"

            ok, err = build_qcore_plugin()
            if not ok:
                ENGINE_STATUS["last_auto_status"] = f"build_failed: {err}"
                print("[AUTO-RELOAD] ❌ Lỗi build:", err)
                continue

            try:
                reload_cmd = 'curl -X POST http://localhost:25575/command -d "plugman reload QCoreBridge"'
                subprocess.run(reload_cmd, shell=True)
                ENGINE_STATUS["last_auto_status"] = "success"
                print("[AUTO-RELOAD] ✅ Reload thành công QCoreBridge.")
            except Exception as e:
                ENGINE_STATUS["last_auto_status"] = f"reload_failed: {e}"
                print("[AUTO-RELOAD] ❌ Lỗi reload:", e)

threading.Thread(target=auto_reload_worker, daemon=True).start()


# =============================================================
# 🌠 DASHBOARD
# =============================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - START_TIME)
    html = f"""
    <html><head><title>Celestial Engine v2.3</title></head>
    <body style='background:black;color:lime;font-family:monospace'>
    <h2>🌌 Celestial Engine v2.3 – Thiên Đạo Toàn Quyền</h2>
    <p><b>Engine ID:</b> {ENGINE_ID}</p>
    <p><b>Connected:</b> {ENGINE_STATUS['connected']}</p>
    <p><b>Uptime:</b> {uptime}s</p>
    <p><b>Last Auto-Reload:</b> {ENGINE_STATUS['last_auto_reload']} | Status: {ENGINE_STATUS['last_auto_status']}</p>
    <hr>
    <h3>🧩 Player States ({len(PLAYER_STATE)})</h3>
    """
    for name, st in PLAYER_STATE.items():
        html += f"<p>👤 <b>{name}</b> → {st['realm']} ({st['energy']:.2f})</p>"
    html += """
    <hr><p><a href='/plugin/patch_queue' style='color:cyan'>→ Patch Queue</a></p>
    <script>setTimeout(()=>location.reload(),5000)</script>
    </body></html>
    """
    return HTMLResponse(html)


print(f"[Celestial Engine v2.3] ✅ Khởi động hoàn tất | ID={ENGINE_ID}")