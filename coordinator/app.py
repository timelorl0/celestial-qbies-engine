from fastapi import FastAPI, Request
from api import system_api
app.include_router(system_api.router)
from api import system_api
app.include_router(system_api.router)
from fastapi.responses import HTMLResponse, JSONResponse
import time, math, threading, json, os, requests, random

app = FastAPI(title='Celestial Engine v1.5 Multi-Node Network Core')
from api import system_api
app.include_router(system_api.router)
from api import system_api
app.include_router(system_api.router)

DATA_PATH = 'coordinator/data/memory.qbies'
NODES_PATH = 'coordinator/data/nodes.qbies'
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

ENGINE_ID = f'CE-{random.randint(1000,9999)}'
BASE_URL = 'https://celestial-qbies-engine.onrender.com'

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

@app.get('/dashboard', response_class=HTMLResponse)
def dashboard():
    uptime = int(time.time() - start_time)
    status = 'Healing...' if healing else 'Stable'
    node_list = '<br>'.join(nodes)
    html = f'''
    <html><head><title>Celestial Engine v1.5 Multi-Node Network</title></head>
    <body style='background:black;color:lime;font-family:monospace'>
    <h2>🌐 Celestial Engine v1.5 Multi-Node Network</h2>
    <p><b>Engine ID:</b> {ENGINE_ID}</p>
    <p>Alpha: {energy['alpha']:.3f}</p>
    <p>Beta: {energy['beta']:.3f}</p>
    <p>Gamma: {energy['gamma']:.3f}</p>
    <p>Entropy: {entropy:.3f}</p>
    <p>Status: {status}</p>
    <p>Uptime: {uptime}s</p>
    <p>(Nodes connected: {len(nodes)})</p>
    <p>{node_list}</p>
    <p>(Quantum Pulse mỗi 10s – Auto-save mỗi 60s)</p>
    <script>setTimeout(()=>{{location.reload()}},5000)</script>
    </body></html>
    '''
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

threading.Thread(target=quantum_core, daemon=True).start()
threading.Thread(target=quantum_network, daemon=True).start()
