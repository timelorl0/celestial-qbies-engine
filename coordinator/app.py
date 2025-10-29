from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import time, math, threading, json, os, requests, random

app = FastAPI(title="Celestial Engine v1.4 Quantum Synchronization Core")

DATA_PATH = "coordinator/data/memory.qbies"
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

# === ĐỊNH DANH ENGINE ===
ENGINE_ID = f"CE-{random.randint(1000,9999)}"

# === KHỞI TẠO HOẶC TẢI DỮ LIỆU CŨ ===
if os.path.exists(DATA_PATH):
    try:
        with open(DATA_PATH, "r") as f:
            saved = json.load(f)
            energy = saved.get("energy", {"alpha": 12.0, "beta": 6.0, "gamma": 3.0})
            entropy = saved.get("entropy", 0.0)
    except:
        energy = {"alpha": 12.0, "beta": 6.0, "gamma": 3.0}
        entropy = 0.0
else:
    energy = {"alpha": 12.0, "beta": 6.0, "gamma": 3.0}
    entropy = 0.0

healing = False
start_time = time.time()

# === DANH SÁCH ENGINE KHÁC (CÓ THỂ MỞ RỘNG) ===
SYNC_NODES = [
    "https://celestial-qbies-engine.onrender.com",  # self-sync (loopback)
]

# === CƠ CHẾ ĐỒNG BỘ NĂNG LƯỢNG LƯỢNG TỬ ===
def quantum_sync():
    global energy, entropy
    while True:
        for node in SYNC_NODES:
            if node.endswith(ENGINE_ID):  # tránh tự gọi chính mình
                continue
            try:
                res = requests.get(f"{node}/sync-data", timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    # Cộng hưởng trung bình năng lượng
                    for k in energy:
                        energy[k] = round((energy[k] + data["energy"][k]) / 2, 3)
                    entropy = round((entropy + data["entropy"]) / 2, 3)
            except Exception:
                pass
        time.sleep(15)

# === CƠ CHẾ DAO ĐỘNG NĂNG LƯỢNG ===
def quantum_core():
    global energy, entropy, healing
    save_timer = 0
    while True:
        total = sum(energy.values())
        entropy = round((math.sin(time.time() / 20) + 1) * total / 200, 3)
        healing = entropy > 0.15
        for k in energy:
            energy[k] = round(max(0, energy[k] - (entropy * (0.03 if healing else 0.01))), 3)
        save_timer += 1
        if save_timer >= 60:
            with open(DATA_PATH, "w") as f:
                json.dump({"energy": energy, "entropy": entropy}, f)
            save_timer = 0
        time.sleep(1)

# === ROUTE DASHBOARD ===
@app.get('/dashboard', response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - start_time)
    status = 'Healing...' if healing else 'Stable'
    html = f"""
    <html>
    <head><title>Celestial Engine v1.4 Quantum Sync</title></head>
    <body style='background-color:black;color:lime;font-family:monospace;'>
    <h2>⚛️ Celestial Engine v1.4 Quantum Synchronization ⚛️</h2>
    <p><b>Engine ID:</b> {ENGINE_ID}</p>
    <p>Alpha: {energy['alpha']:.3f}</p>
    <p>Beta: {energy['beta']:.3f}</p>
    <p>Gamma: {energy['gamma']:.3f}</p>
    <p>Entropy: {entropy:.3f}</p>
    <p>Status: {status}</p>
    <p>Uptime: {uptime}s</p>
    <p>(Quantum Sync active — cập nhật mỗi 15s)</p>
    <p>(Memory.QBIES active — Auto-save mỗi 60s)</p>
    <script>setTimeout(()=>{{location.reload()}},5000)</script>
    </body></html>
    """
    return HTMLResponse(html)

# === ROUTE ĐỒNG BỘ DỮ LIỆU ===
@app.get("/sync-data")
def sync_data():
    return JSONResponse({"engine_id": ENGINE_ID, "energy": energy, "entropy": entropy})

threading.Thread(target=quantum_core, daemon=True).start()
threading.Thread(target=quantum_sync, daemon=True).start()
