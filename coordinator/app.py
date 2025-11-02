# Celestial Engine v1.6 – Unified with Thiên Đạo Toàn Quyền 🌌
# -------------------------------------------------------------
# Toàn quyền vận hành: lượng tử – năng lượng – tu luyện – hiển thị
# © Celestial QBIES Universe Engine

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import time, math, threading, json, os, requests, random
from datetime import datetime

# ===== Core Init =====
app = FastAPI(title='Celestial Engine v1.6 – Unified Core')

DATA_PATH = 'coordinator/data/memory.qbies'
NODES_PATH = 'coordinator/data/nodes.qbies'
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

ENGINE_ID = f'CE-{random.randint(1000,9999)}'
BASE_URL = 'https://celestial-qbies-engine.onrender.com'
ENGINE_STATUS = "stable"
ENGINE_START = datetime.utcnow()

# ===== Data Management =====
def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except:
        pass
    return default

energy = load_json(DATA_PATH, {'alpha': 12.0, 'beta': 6.0, 'gamma': 3.0})
entropy = energy.get('entropy', 0.0)
nodes = load_json(NODES_PATH, [BASE_URL])

healing = False
start_time = time.time()

def save_state():
    with open(DATA_PATH, 'w') as f:
        json.dump({'energy': energy, 'entropy': entropy}, f)
    with open(NODES_PATH, 'w') as f:
        json.dump(nodes, f)

# ===== Core Quantum Threads =====
def quantum_core():
    global energy, entropy, healing
    tick = 0
    while True:
        total = sum(energy.values())
        entropy = round((math.sin(time.time() / 20) + 1) * total / 200, 3)
        healing = entropy > 0.15
        for k in energy:
            energy[k] = round(max(0, energy[k] - (entropy * (0.03 if healing else 0.01))), 3)
        tick += 1
        if tick >= 60:
            save_state()
            tick = 0
        time.sleep(1)

def quantum_network():
    global energy, entropy, nodes
    while True:
        for node in nodes:
            if node == BASE_URL:
                continue
            try:
                res = requests.get(f'{node}/sync-data', timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    for k in energy:
                        energy[k] = round((energy[k] + data['energy'][k]) / 2, 3)
                    entropy = round((entropy + data['entropy']) / 2, 3)
            except:
                pass
        time.sleep(10)

# ===== Import Routers =====
from coordinator.api import system_api
app.include_router(system_api.router)
from coordinator.api import nodes_api
app.include_router(nodes_api.router)

# =============================================================
# ☯️ THIÊN ĐẠO TOÀN QUYỀN – HÒA NHẬP
# =============================================================

REALMS = [
    {"name": "Phàm Nhân", "req": 0, "color": "§7"},
    {"name": "Nhập Môn", "req": 50, "color": "§9"},
    {"name": "Trúc Cơ", "req": 200, "color": "§a"},
    {"name": "Ngưng Tuyền", "req": 800, "color": "§e"},
    {"name": "Kim Đan", "req": 2500, "color": "§6"},
    {"name": "Nguyên Anh", "req": 6000, "color": "§d"},
    {"name": "Hóa Thần", "req": 15000, "color": "§5"},
]

PLAYER_STORE = {}

def get_realm_for_energy(e):
    current = REALMS[0]
    for r in REALMS:
        if e >= r["req"]:
            current = r
        else:
            break
    return current

def make_action(act, target, **params):
    return {"action": act, "target": target, "params": params}

@app.post("/process_event")
async def process_event(req: Request):
    ev = await req.json()
    name = ev.get("player", "Unknown")
    p = PLAYER_STORE.setdefault(name, {"energy": 0.0, "realm_idx": 0, "karma": 0.0, "auto": True})
    actions = []

    if ev.get("type") in ("tick", "tu_luyen"):
        gain = ev.get("energy", random.uniform(0.8, 1.4))
        p["energy"] += gain
        p["karma"] = ev.get("karma", p["karma"])

    realm = get_realm_for_energy(p["energy"])
    p["realm_idx"] = next(i for i, r in enumerate(REALMS) if r["name"] == realm["name"])

    actions.append(make_action(
        "set_ui", name,
        energy=round(p["energy"], 1),
        required=REALMS[min(p["realm_idx"] + 1, len(REALMS) - 1)]["req"],
        realm=realm["name"],
        color=realm["color"],
        place_over_exp=True
    ))

    next_realm = REALMS[p["realm_idx"] + 1] if p["realm_idx"] + 1 < len(REALMS) else None
    if next_realm and p["energy"] >= next_realm["req"]:
        p["energy"] = 0.0
        p["realm_idx"] += 1
        new_realm = REALMS[p["realm_idx"]]
        actions += [
            make_action("title", name, title="⚡ ĐỘT PHÁ!", subtitle=new_realm["name"]),
            make_action("play_sound", name, sound="ENTITY_PLAYER_LEVELUP", volume=1.2, pitch=0.6),
            make_action("particle", name, type="TOTEM", count=60, offset=[0, 1.5, 0]),
            make_action("auto_continue", name, realm=new_realm["name"])
        ]

    if ev.get("type") == "tu_luyen":
        actions += [
            make_action("particle", name, type="ENCHANTMENT_TABLE", count=16, offset=[0, 1.0, 0]),
            make_action("play_sound", name, sound="BLOCK_ENCHANTMENT_TABLE_USE", volume=0.7, pitch=1.2)
        ]

    return JSONResponse({"actions": actions, "realm": realm["name"], "energy": p["energy"]})

@app.get("/ping")
def ping():
    return JSONResponse({
        "ok": True,
        "time": time.time(),
        "realms": len(REALMS),
        "players": len(PLAYER_STORE),
        "entropy": entropy
    })

# =============================================================
# 🔗 CẦU NỐI QBIESLINK – MINECRAFT BRIDGE
# =============================================================

LINK_STATUS = {
    "minecraft_connected": False,
    "last_ping": None,
    "plugin_version": None,
    "player_count": 0,
}

@app.post("/plugin/ping")
async def plugin_ping(req: Request):
    data = await req.json()
    LINK_STATUS["minecraft_connected"] = True
    LINK_STATUS["last_ping"] = time.strftime("%H:%M:%S")
    LINK_STATUS["plugin_version"] = data.get("version", "unknown")
    LINK_STATUS["player_count"] = data.get("players", 0)
    return {"ok": True, "msg": "Ping received", "time": LINK_STATUS["last_ping"]}

@app.post("/plugin/data")
async def plugin_data(req: Request):
    data = await req.json()
    print("[QBiesLink] Data received:", data)
    return {"ok": True, "status": "stored"}

@app.get("/link_status")
def link_status():
    return LINK_STATUS

def watchdog():
    while True:
        if LINK_STATUS["last_ping"]:
            try:
                t = time.strptime(LINK_STATUS["last_ping"], "%H:%M:%S")
                delta = time.time() - time.mktime(t)
                if delta > 10:
                    LINK_STATUS["minecraft_connected"] = False
            except:
                pass
        time.sleep(5)

threading.Thread(target=watchdog, daemon=True).start()

# =============================================================
# 🧩 DASHBOARD – HỢP NHẤT THIÊN ĐẠO
# =============================================================

@app.get('/dashboard', response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - start_time)
    status = 'Healing...' if healing else 'Stable'
    node_list = '<br>'.join(nodes)
    mc_status = '🟢 Connected' if LINK_STATUS['minecraft_connected'] else '🔴 Disconnected'
    html = f"""
    <html><head><title>Celestial Engine v1.6 Unified</title></head>
    <body style='background:black;color:lime;font-family:monospace'>
    <h2>🌌 Celestial Engine v1.6 – Thiên Đạo Toàn Quyền</h2>
    <p><b>Engine ID:</b> {ENGINE_ID}</p>
    <p>Alpha: {energy['alpha']:.3f}</p>
    <p>Beta: {energy['beta']:.3f}</p>
    <p>Gamma: {energy['gamma']:.3f}</p>
    <p>Entropy: {entropy:.3f}</p>
    <p>Status: {status}</p>
    <p>Uptime: {uptime}s</p>
    <p>(Nodes connected: {len(nodes)})</p>
    <p>{node_list}</p>
    <hr>
    <h3>⚡ Thiên Đạo – Realms & Energy</h3>
    <p>Người chơi đang được giám sát: {len(PLAYER_STORE)}</p>
    <p>Hiện có {len(REALMS)} cảnh giới được kích hoạt</p>
    <hr>
    <h3>🔗 QBiesLink Bridge</h3>
    <p>Trạng thái plugin: {mc_status}</p>
    <p>Phiên bản: {LINK_STATUS['plugin_version']}</p>
    <p>Người chơi online: {LINK_STATUS['player_count']}</p>
    <p>Lần ping gần nhất: {LINK_STATUS['last_ping']}</p>
    <p><a href='/ping' style='color:cyan'>→ Ping Test</a></p>
    <script>setTimeout(()=>{{location.reload()}},4000)</script>
    </body></html>
    """
    return HTMLResponse(html)

@app.get('/sync-data')
def sync_data():
    return JSONResponse({'engine_id': ENGINE_ID, 'energy': energy, 'entropy': entropy})

@app.post('/register-node')
async def register_node(req: Request):
    data = await req.json()
    node_url = data.get('url')
    if node_url and node_url not in nodes:
        nodes.append(node_url)
        save_state()
    return JSONResponse({'registered': nodes})

# ===== START THREADS =====
threading.Thread(target=quantum_core, daemon=True).start()
threading.Thread(target=quantum_network, daemon=True).start()

print(f"[Celestial Engine] 🌠 Boot complete | ID={ENGINE_ID}")