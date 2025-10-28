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

threading.Thread(target=quantum_core, daemon=True).start()

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

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    status_text = "Healing..." if healing else "Stable"
    html = """
    <html>
    <head><meta http-equiv=refresh content=5>
    <style>
        body { font-family: monospace; background: #000; color: #0f0; text-align: center; }
    </style></head>
    <body>
        <h2>🌌 Celestial Engine v1.3 Auto-Heal Quantum Core 🌌</h2>
        <p>Alpha: {alpha}</p>
        <p>Beta: {beta}</p>
        <p>Gamma: {gamma}</p>
        <p>Entropy: {entropy}</p>
        <p>Status: {status}</p>
        <p>Uptime: {uptime} s</p>
        <p>(Auto-refresh mỗi 5 giây)</p>
    </body></html>
    """.format(
        alpha=energy["alpha"],
        beta=energy["beta"],
        gamma=energy["gamma"],
        entropy=entropy,
        status=status_text,
        uptime=int(time.time() - start_time)
    )
    return html
