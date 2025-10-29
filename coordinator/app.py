
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import time, math, threading

app = FastAPI(title="Celestial Engine v1.3 Auto-Heal Quantum Core")

energy = {"alpha": 12.0, "beta": 6.0, "gamma": 3.0}
entropy = 0.0
healing = False
start_time = time.time()

def quantum_core():
    global energy, entropy, healing
    while True:
        total = sum(energy.values())
        # Tính entropy dao động
        entropy = round((math.sin(time.time() / 20) + 1) * total / 200, 3)
        
        # Nếu entropy quá cao thì tự chữa lành
        if entropy > 0.15:
            healing = True
            for k in energy:
                energy[k] = round(max(0, energy[k] - entropy * 0.03), 3)
            entropy = round(max(0, entropy - 0.01), 3)
        else:
            healing = False

        time.sleep(2)

# Chạy vòng lặp lượng tử
threading.Thread(target=quantum_core, daemon=True).start()

@app.get("/status")
def status():
    uptime = int(time.time() - start_time)
    return {
        "engine": "Celestial QBIES",
        "version": "v1.3 Auto-Heal Quantum Core",
        "energy": energy,
        "entropy": entropy,
        "healing": healing,
        "uptime": uptime
    }

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - start_time)
    html = f"""
    <html><head><title>Celestial Engine v1.3 Auto-Heal Quantum Core</title>
    <meta http-equiv=refresh content=5>
    <style>
        body {{
            background-color: #000;
            color: #0f0;
            font-family: monospace;
            text-align: center;
        }}
    </style></head>
    <body>
    <h2>🩵 Celestial Engine v1.3 Auto-Heal Quantum Core 🩵</h2>
    <p>Alpha: {{energy[alpha]:.3f}}</p>
    <p>Beta: {{energy[beta]:.3f}}</p>
    <p>Gamma: {{energy[gamma]:.3f}}</p>
    <p>Entropy: {{entropy:.3f}}</p>
    <p>Status: {{Healing... if healing else Stable}}</p>
    <p>Uptime: {{uptime}}s</p>
    <p>(Auto-refresh mỗi 5 giây)</p>
    </body></html>
    """
    return HTMLResponse(content=html)

