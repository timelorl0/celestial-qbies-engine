from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import threading, time, math

app = FastAPI(title='Celestial Engine v1.2 Quantum Flow Loop')

energy = {'alpha': 12.0, 'beta': 6.0, 'gamma': 3.0}
entropy = 0.0
start_time = time.time()

def quantum_flow_loop():
    global energy, entropy
    while True:
        total = sum(energy.values())
        entropy = round((math.sin(time.time() / 30) + 1) * total / 100, 3)
        for k in energy:
            energy[k] = round(max(0.0, energy[k] + math.sin(time.time() / 10) * 0.05), 3)
        time.sleep(5)

threading.Thread(target=quantum_flow_loop, daemon=True).start()

@app.get('/status')
def status():
    uptime = int(time.time() - start_time)
    return {
        'engine': 'Celestial QBIES',
        'version': 'v1.2-quantum-flow-loop',
        'energy': energy,
        'entropy': entropy,
        'uptime': uptime
    }

@app.get('/dashboard', response_class=HTMLResponse)
def dashboard():
    html = f'''
    <html><head><title>Celestial Engine Dashboard</title>
    <meta http-equiv=refresh content=5>
    <style>body{{font-family:monospace;background:#000;color:#0f0;text-align:center;}}</style>
    </head><body>
    <h2>⚛ Celestial Engine Quantum Dashboard ⚛</h2>
    <p>Alpha: {energy['alpha']:.3f}</p>
    <p>Beta: {energy['beta']:.3f}</p>
    <p>Gamma: {energy['gamma']:.3f}</p>
    <p>Entropy: {entropy:.3f}</p>
    <p>Uptime: {int(time.time()-start_time)}s</p>
    <p>(auto-refresh mỗi 5s)</p>
    </body></html>
    '''
    return HTMLResponse(html)
