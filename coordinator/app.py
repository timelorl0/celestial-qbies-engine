from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import time, math, threading, json, os

app = FastAPI(title='Celestial Engine v1.3.1 Auto-Heal + Memory QBIES Core')

# === ĐƯỜNG DẪN FILE LƯU DỮ LIỆU ===
DATA_PATH = "coordinator/data/memory.qbies"
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

# === KHỞI TẠO GIÁ TRỊ BAN ĐẦU ===
if os.path.exists(DATA_PATH):
    try:
        with open(DATA_PATH, "r") as f:
            saved = json.load(f)
            energy = saved.get("energy", {"alpha": 12.0, "beta": 6.0, "gamma": 3.0})
            entropy = saved.get("entropy", 0.0)
    except Exception:
        energy = {"alpha": 12.0, "beta": 6.0, "gamma": 3.0}
        entropy = 0.0
else:
    energy = {"alpha": 12.0, "beta": 6.0, "gamma": 3.0}
    entropy = 0.0

healing = False
start_time = time.time()

# === CHU TRÌNH NĂNG LƯỢNG ===
def quantum_core():
    global energy, entropy, healing
    save_timer = 0
    while True:
        total = sum(energy.values())
        entropy = round((math.sin(time.time() / 20) + 1) * total / 200, 3)
        healing = entropy > 0.15
        for k in energy:
            energy[k] = round(max(0, energy[k] - (entropy * (0.03 if healing else 0.01))), 3)
        # Lưu dữ liệu mỗi 60 giây
        save_timer += 1
        if save_timer >= 60:
            try:
                with open(DATA_PATH, "w") as f:
                    json.dump({"energy": energy, "entropy": entropy}, f)
            except Exception as e:
                print(f"[WARN] Memory save failed: {e}")
            save_timer = 0
        time.sleep(1)

# === DASHBOARD HIỂN THỊ ===
@app.get('/dashboard', response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - start_time)
    status = 'Healing...' if healing else 'Stable'
    html = f"""
    <html>
    <head><title>Celestial Engine v1.3.1 Memory QBIES</title></head>
    <body style='background-color:black;color:lime;font-family:monospace;'>
    <h2>🌌 Celestial Engine v1.3.1 Auto-Heal + Memory QBIES Core 🌌</h2>
    <p>Alpha: {energy['alpha']:.3f}</p>
    <p>Beta: {energy['beta']:.3f}</p>
    <p>Gamma: {energy['gamma']:.3f}</p>
    <p>Entropy: {entropy:.3f}</p>
    <p>Status: {status}</p>
    <p>Uptime: {uptime}s</p>
    <p>(Memory.QBIES active — Auto-save mỗi 60s)</p>
    <script>setTimeout(()=>{{location.reload()}},5000)</script>
    </body></html>
    """
    return HTMLResponse(html)

threading.Thread(target=quantum_core, daemon=True).start()
