from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import time, math, threading

app = FastAPI(title='Celestial Engine v1.3 Auto-Heal Quantum Core')

energy = {'alpha': 12.0, 'beta': 6.0, 'gamma': 3.0}
entropy = 0.0
healing = False
start_time = time.time()

def quantum_core():
    global energy, entropy, healing
    while True:
        total = sum(energy.values())
        entropy = round((math.sin(time.time() / 20) + 1) * total / 200, 3)
        healing = entropy > 0.15
        for k in energy:
            energy[k] = round(max(0, energy[k] - (entropy * (0.03 if healing else 0.01))), 3)
        time.sleep(1)

@app.get('/dashboard', response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - start_time)
    status = 'Healing...' if healing else 'Stable'
    html = f"""
    <html>
    <head><title>Celestial Engine v1.3 Auto-Heal Quantum Core</title></head>
    <body style='background-color:black;color:lime;font-family:monospace;'>
    <h2>🌌 Celestial Engine v1.3 Auto-Heal Quantum Core 🌌</h2>
    <p>Alpha: {energy['alpha']:.3f}</p>
    <p>Beta: {energy['beta']:.3f}</p>
    <p>Gamma: {energy['gamma']:.3f}</p>
    <p>Entropy: {entropy:.3f}</p>
    <p>Status: {status}</p>
    <p>Uptime: {uptime}s</p>
    <p>(Auto-refresh mỗi 5 giây)</p>
    <script>setTimeout(()=>{{location.reload()}},5000)</script>
    </body></html>
    """
    return HTMLResponse(html)

threading.Thread(target=quantum_core, daemon=True).start()
