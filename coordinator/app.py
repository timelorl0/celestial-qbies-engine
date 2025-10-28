from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import time, math, threading

app = FastAPI(title="Celestial Engine v1.3 Auto-Heal Quantum Core")

energy = {"alpha": 12.0, "beta": 6.0, "gamma": 3.0}
entropy = 0.0
start_time = time.time()
healing = False

def quantum_core():
    global energy, entropy, healing
    while True:
        try:
            total = sum(energy.values())
            entropy = round(abs(math.sin(time.time() / 25)) * total / 100, 3)
            if entropy > 0.5:
                healing = True
                for k in energy:
                    energy[k] = round(energy[k] + 0.1, 3)
                entropy = max(0.0, entropy - 0.05)
            else:
                healing = False
                for k in energy:
                    energy[k] = round(max(0, energy[k] + math.sin(time.time() / 10) * 0.05), 3)
            time.sleep(3)
        except Exception as e:
            print("⚠️ Core loop error:", e)
            time.sleep(2)

threading.Thread(target=quantum_core, daemon=True).start()

@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def dashboard():
    # Nếu năng lượng chưa khởi tạo thì dùng giá trị mặc định
    a = energy.get("alpha", 0.0)
    b = energy.get("beta", 0.0)
    g = energy.get("gamma", 0.0)
    e = entropy
    s = "Healing..." if healing else "Stable"
    up = int(time.time() - start_time)

    html = f"""
    <html><head><meta http-equiv=refresh content=5>
    <style>body{{background:#000;color:#0f0;text-align:center;font-family:monospace}}</style>
    </head><body>
    <h2>🌌 Celestial Engine v1.3 Auto-Heal Quantum Core 🌌</h2>
    <p>Alpha: {a}</p>
    <p>Beta: {b}</p>
    <p>Gamma: {g}</p>
    <p>Entropy: {e}</p>
    <p>Status: {s}</p>
    <p>Uptime: {up} s</p>
    <p>(Auto-refresh mỗi 5 giây)</p>
    </body></html>"""
    return html

@app.get("/status")
def status():
    return {
        "engine": "Celestial Qbies",
        "version": "v1.3 Auto-Heal Quantum Core",
        "energy": energy,
        "entropy": entropy,
        "healing": healing,
        "uptime": int(time.time() - start_time)
    }
