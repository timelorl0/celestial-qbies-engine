# app.py
# Celestial Engine - main API + plugin reload receiver + simple dashboard
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, subprocess, shutil, hashlib
from pathlib import Path
import requests

# Config (edit / set env vars as needed)
BASE_DIR = Path(__file__).parent
UPDATES_DIR = BASE_DIR / "render_updates"
METADATA_PATH = BASE_DIR / "render_meta.json"
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")  # set env or paste string here
FALIX_API = os.environ.get("FALIX_API", "http://localhost:25575/command")
AUTO_RELOAD_SECRET = os.environ.get("AUTO_RELOAD_SECRET", "celestial-secret")

os.makedirs(UPDATES_DIR, exist_ok=True)

app = FastAPI(title="Celestial Engine v3.x - Render")

# in-memory players
PLAYER_STATE = {}
REALMS = ["Phàm Nhân","Nhập Môn","Luyện Khí","Trúc Cơ","Kết Đan","Nguyên Anh","Hóa Thần","Luyện Hư","Hợp Thể","Đại Thừa","Độ Kiếp"]
REALM_THRESHOLDS = [0,50,200,800,3000,8000,20000,50000,120000,300000,1000000]

def save_meta():
    try:
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"players": PLAYER_STATE, "time": time.time()}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def post_discord(msg: str):
    if not DISCORD_WEBHOOK:
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=5)
    except Exception:
        pass

@app.post("/process_event")
async def process_event(req: Request):
    try:
        data = await req.json()
    except:
        raise HTTPException(400, "invalid json")
    name = data.get("player", "Unknown")
    gain = float(data.get("energy", 1.0))
    p = PLAYER_STATE.setdefault(name, {"path": None, "energy": 0.0, "realm": "Phàm Nhân"})
    # choose path logic (if client asked)
    if not p.get("path"):
        return {"choose_path": True, "options": [{"id":"tutien","name":"Tu Tiên"},{"id":"tudao","name":"Tu Đạo"},{"id":"tuma","name":"Tu Ma"},{"id":"tuluyen","name":"Tu Tự Do"}]}
    p["energy"] += gain
    # compute realm
    idx = 0
    for i, th in enumerate(REALM_THRESHOLDS):
        if p["energy"] >= th:
            idx = i
    new_realm = REALMS[min(idx, len(REALMS)-1)]
    p["realm"] = new_realm
    save_meta()
    actions = [{"action":"set_ui","target":name,"params":{"path":p["path"],"realm":new_realm,"energy":round(p["energy"],2)}}]
    # if reached next threshold -> create breakthrough actions
    if idx + 1 < len(REALM_THRESHOLDS) and p["energy"] >= REALM_THRESHOLDS[min(idx+1,len(REALM_THRESHOLDS)-1)]:
        # reward / actions
        actions += [
            {"action":"title","target":name,"params":{"title":"⚡ ĐỘT PHÁ!","subtitle":REALMS[min(idx+1,len(REALMS)-1)]}},
            {"action":"particle","target":name,"params":{"type":"TOTEM","count":80}},
            {"action":"sound","target":name,"params":{"sound":"ENTITY_PLAYER_LEVELUP","volume":1.2}}
        ]
        p["energy"] = 0.0
        p["realm"] = REALMS[min(idx+1,len(REALMS)-1)]
        save_meta()
    return {"ok": True, "player": name, "realm": p["realm"], "actions": actions}

@app.post("/choose_path")
async def choose_path(req: Request):
    data = await req.json()
    name = data.get("player")
    path = data.get("path")
    if not name or not path:
        raise HTTPException(400, "missing fields")
    p = PLAYER_STATE.setdefault(name, {"path": None, "energy":0.0, "realm":"Phàm Nhân"})
    p["path"] = path
    save_meta()
    return {"ok":True, "message": f"{name} đã chọn {path}"}

@app.post("/plugin/ping")
async def plugin_ping(req: Request):
    # simple ping used by falix plugin to signal alive
    return {"ok": True, "time": time.time()}

@app.post("/auto_reload")
async def auto_reload(req: Request):
    # Endpoint used by plugin to request reload; protect by secret optionally
    data = await req.json()
    secret = data.get("secret", "")
    if AUTO_RELOAD_SECRET and secret != AUTO_RELOAD_SECRET:
        raise HTTPException(403, "forbidden")
    # respond with instruction to plugin or ack
    return {"ok": True, "message":"Render received reload request"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    uptime = int(time.time() - app.state.start_time) if hasattr(app.state, "start_time") else 0
    html = f"<html><body style='font-family:monospace;background:#0b0b0b;color:#9ff;'><h2>Celestial Engine (Render)</h2><p>Uptime: {uptime}s</p><hr>"
    html += f"<h3>Players: {len(PLAYER_STATE)}</h3>"
    for n,s in PLAYER_STATE.items():
        html += f"<p>{n}: {s.get('path','-')} | {s.get('realm','Phàm Nhân')} ({s.get('energy',0):.1f})</p>"
    html += "</body></html>"
    return HTMLResponse(html)

# -------------- Self-update monitor for Render (simple) --------------
def file_hash(path: Path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                b = f.read(4096)
                if not b: break
                h.update(b)
        return h.hexdigest()
    except:
        return None

def render_update_worker():
    # keep map of filename->hash
    known = {}
    # load existing
    for p in UPDATES_DIR.iterdir():
        if p.is_file():
            known[p.name] = file_hash(p)
    while True:
        try:
            for p in UPDATES_DIR.iterdir():
                if not p.is_file(): continue
                h = file_hash(p)
                if p.name not in known or known[p.name] != h:
                    # new/changed file detected
                    try:
                        # simple policy: if app.py changed -> attempt to validate by syntax check
                        if p.name.endswith(".py"):
                            # run syntax check
                            r = subprocess.run(["python","-m","py_compile", str(p)], capture_output=True, text=True)
                            if r.returncode != 0:
                                post_discord(f"[RenderUpdater] Syntax error in {p.name}: {r.stderr[:300]}")
                                known[p.name] = h
                                continue
                        # backup and copy into place (overwrite)
                        dest = BASE_DIR / p.name
                        backup = BASE_DIR / f"{p.name}.bak.{int(time.time())}"
                        if dest.exists():
                            shutil.copy2(dest, backup)
                        shutil.copy2(p, dest)
                        known[p.name] = h
                        post_discord(f"[RenderUpdater] Applied update {p.name}")
                    except Exception as e:
                        post_discord(f"[RenderUpdater] Failed to apply {p.name}: {e}")
            time.sleep(4)
        except Exception:
            time.sleep(4)

# record start time
app.state.start_time = time.time()
# start background thread
threading.Thread(target=render_update_worker, daemon=True).start()

print(f"[Celestial Render] ready")