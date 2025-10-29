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
        entropy = round((math.sin(time.time() / 20) + 1) * total / 200, 3)
        if entropy > 0.15:
            healing = True
            for k in energy:
                energy[k] = round(max(0, energy[k] - entropy * 0.03), 3)
            entropy = round(max(0, entropy - 0.01), 3)
        else:
            healing = False
        time.sleep(2)

threading.Thread(target=quantum_core, daemon=True).start()

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - start_time)
    html = (
        "<html><head><title>Celestial Engine v1.3 Auto-Heal Quantum Core</title>"
        "<meta http-equiv=refresh content=5>"
        "<style>body {background-color:#000;color:#0f0;font-family:monospace;text-align:center;}</style></head><body>"
        "<h2>🩵 Celestial Engine v1.3 Auto-Heal Quantum Core 🩵</h2>"
        f"<p>Alpha: {energy[alpha]:.3f}</p>"
        f"<p>Beta: {energy[beta]:.3f}</p>"
        f"<p>Gamma: {energy[gamma]:.3f}</p>"
        f"<p>Entropy: {entropy:.3f}</p>"
        f"<p>Status: {'Healing...' if healing else 'Stable'}</p>"
        f"<p>Uptime: {uptime}s</p>"
        "<p>(Auto-refresh mỗi 5 giây)</p></body></html>"
    )
    return HTMLResponse(content=html)
