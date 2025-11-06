# app.py
# Celestial Engine v3.x – Render Core with QBIES + Fractal Integration + Dashboard

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
import os, json, time, threading, subprocess, shutil, hashlib, requests
from pathlib import Path

# ===============================[ CONFIG ]===============================
BASE_DIR = Path(__file__).parent
UPDATES_DIR = BASE_DIR / "render_updates"
METADATA_PATH = BASE_DIR / "render_meta.json"
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
FALIX_API = os.environ.get("FALIX_API", "http://localhost:25575/command")
AUTO_RELOAD_SECRET = os.environ.get("AUTO_RELOAD_SECRET", "celestial-secret")

os.makedirs(UPDATES_DIR, exist_ok=True)
os.makedirs(BASE_DIR / "cache/snapshots", exist_ok=True)

app = FastAPI(title="Celestial Engine v3.x - Render")

# ===============================[ FRACTAL ENGINE + QBIES ]===============================
import zlib, json as js

class QBIESCompressor:
    def compress(self, obj):
        raw = js.dumps(obj, ensure_ascii=False).encode("utf-8")
        return zlib.compress(raw, level=6)
    def decompress(self, data):
        raw = zlib.decompress(data)
        return js.loads(raw.decode("utf-8"))

def write_snapshot(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    comp = QBIESCompressor().compress(data)
    with open(path, "wb") as f: f.write(comp)

def read_snapshot(path):
    comp = open(path, "rb").read()
    return QBIESCompressor().decompress(comp)

class FractalEngine:
    def __init__(self, cache_dir="cache/snapshots", filename="universe.qbie"):
        self.cache_dir = cache_dir
        self.filename = filename
        self.path = os.path.join(cache_dir, filename)
        self.universe = {"meta": {"genesis": time.time()}, "players": {}}
        self.lock = threading.RLock()
        self.dirty = False
        self.running = False
        self.autosave_interval = 30

    def load_universe(self):
        if os.path.exists(self.path):
            try:
                self.universe = read_snapshot(self.path)
                print("🌌 [Fractal] Đã nạp snapshot:", self.path)
            except Exception as e:
                print("⚠ [Fractal] Không thể nạp snapshot:", e)
        else:
            print("✨ [Fractal] Bắt đầu vũ trụ mới (GENESIS).")
        self.start_autosave()

    def evolve(self, ctx=None):
        with self.lock:
            now = time.time()
            meta = self.universe.setdefault("meta", {})
            meta["last_tick"] = now
            players = self.universe.setdefault("players", {})
            if ctx and "player" in ctx:
                name = ctx["player"]
                info = players.setdefault(name, {"energy": 0, "realm": "Phàm Nhân", "visits": 0})
                info["visits"] += 1
                info["energy"] += ctx.get("energy", 0)
                info["realm"] = ctx.get("realm", info["realm"])
            self.dirty = True

    def save_universe(self):
        with self.lock:
            write_snapshot(self.path, self.universe)
            self.dirty = False
            print("💾 [Fractal] Snapshot saved.")

    def start_autosave(self):
        if self.running: return
        self.running = True
        def loop():
            while self.running:
                time.sleep(self.autosave_interval)
                if self.dirty:
                    self.save_universe()
        threading.Thread(target=loop, daemon=True).start()

    def stop_autosave(self):
        self.running = False
        self.save_universe()
        print("🛑 [Fractal] Autosave stopped.")

fractal_engine = FractalEngine()

@app.on_event("startup")
async def startup_event():
    print("🚀 Render khởi động – tải Fractal Universe...")
    fractal_engine.load_universe()
    fractal_engine.evolve({"startup": True})

@app.on_event("shutdown")
async def shutdown_event():
    fractal_engine.stop_autosave()
# =======================================================================


# ===============================[ PLAYER SYSTEM ]===============================
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
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=5)
    except Exception:
        pass

# ===============================[ API ENDPOINTS ]===============================
@app.post("/process_event")
async def process_event(req: Request):
    try:
        data = await req.json()
    except:
        raise HTTPException(400, "invalid json")

    name = data.get("player", "Unknown")
    gain = float(data.get("energy", 1.0))
    p = PLAYER_STATE.setdefault(name, {"path": None, "energy": 0.0, "realm": "Phàm Nhân"})

    if not p.get("path"):
        return {"choose_path": True, "options": [
            {"id":"tutien","name":"Tu Tiên"},
            {"id":"tudao","name":"Tu Đạo"},
            {"id":"tuma","name":"Tu Ma"},
            {"id":"tuluyen","name":"Tu Tự Do"}
        ]}

    p["energy"] += gain
    fractal_engine.evolve({"player": name, "energy": gain, "realm": p["realm"]})

    idx = 0
    for i, th in enumerate(REALM_THRESHOLDS):
        if p["energy"] >= th: idx = i
    new_realm = REALMS[min(idx, len(REALMS)-1)]
    p["realm"] = new_realm
    save_meta()

    actions = [{"action":"set_ui","target":name,"params":{"path":p["path"],"realm":new_realm,"energy":round(p["energy"],2)}}]

    if idx + 1 < len(REALM_THRESHOLDS) and p["energy"] >= REALM_THRESHOLDS[min(idx+1,len(REALM_THRESHOLDS)-1)]:
        actions += [
            {"action":"title","target":name,"params":{"title":"⚡ ĐỘT PHÁ!","subtitle":REALMS[min(idx+1,len(REALM_THRESHOLDS)-1)]}},
            {"action":"particle","target":name,"params":{"type":"TOTEM","count":80}},
            {"action":"sound","target":name,"params":{"sound":"ENTITY_PLAYER_LEVELUP","volume":1.2}}
        ]
        p["energy"] = 0.0
        p["realm"] = REALMS[min(idx+1,len(REALM_THRESHOLDS)-1)]
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

@app.get("/dashboard/data")
async def fractal_data():
    u = fractal_engine.universe
    players = u.get("players", {})
    realms = {}
    for p in players.values():
        r = p.get("realm","Phàm Nhân")
        realms[r] = realms.get(r,0)+1
    return {
        "players": len(players),
        "realms": realms,
        "last_tick": u.get("meta",{}).get("last_tick",0),
        "uptime": int(time.time()-u.get("meta",{}).get("genesis",time.time()))
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    html = """
    <html><head>
    <title>Celestial Engine Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head><body style='background:#0b0b0b;color:#9ff;font-family:monospace;'>
    <h2>🌌 Celestial Engine – Fractal Universe Dashboard</h2>
    <canvas id='realmChart' width='600' height='300'></canvas>
    <p id='info'></p>
    <script>
    async function update() {
        const res = await fetch('/dashboard/data');
        const d = await res.json();
        document.getElementById('info').innerText =
            `👥 Người chơi: ${d.players} | ⏱ Uptime: ${d.uptime}s | 🧬 Lần tiến hoá: ${new Date(d.last_tick*1000).toLocaleTimeString()}`;
        const ctx = document.getElementById('realmChart').getContext('2d');
        const data = {
            labels: Object.keys(d.realms),
            datasets: [{label:'Người trong cảnh giới',data:Object.values(d.realms)}]
        };
        if(window.chart) { window.chart.data=data; window.chart.update(); }
        else window.chart = new Chart(ctx,{type:'bar',data});
    }
    update(); setInterval(update,10000);
    </script></body></html>
    """
    return HTMLResponse(html)

# ===============================[ AUTO-UPDATER ]===============================
def file_hash(path: Path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for b in iter(lambda: f.read(4096), b""): h.update(b)
        return h.hexdigest()
    except: return None

def render_update_worker():
    known = {}
    for p in UPDATES_DIR.iterdir():
        if p.is_file(): known[p.name] = file_hash(p)
    while True:
        try:
            for p in UPDATES_DIR.iterdir():
                if not p.is_file(): continue
                h = file_hash(p)
                if p.name not in known or known[p.name] != h:
                    try:
                        if p.name.endswith(".py"):
                            r = subprocess.run(["python","-m","py_compile", str(p)], capture_output=True, text=True)
                            if r.returncode != 0:
                                post_discord(f"[RenderUpdater] Syntax error in {p.name}: {r.stderr[:300]}")
                                known[p.name] = h
                                continue
                        dest = BASE_DIR / p.name
                        backup = BASE_DIR / f"{p.name}.bak.{int(time.time())}"
                        if dest.exists(): shutil.copy2(dest, backup)
                        shutil.copy2(p, dest)
                        known[p.name] = h
                        post_discord(f"[RenderUpdater] Applied update {p.name}")
                    except Exception as e:
                        post_discord(f"[RenderUpdater] Failed to apply {p.name}: {e}")
            time.sleep(4)
        except Exception:
            time.sleep(4)

app.state.start_time = time.time()
threading.Thread(target=render_update_worker, daemon=True).start()

print(f"[Celestial Render] ready")