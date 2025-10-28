from fastapi import FastAPI, Request
import os, time, threading, requests

# ===============================
# Celestial Engine v1.0 Stable
# ===============================
app = FastAPI(title='Celestial QBIES Engine')
start_time = time.time()

CEL_ENGINE_VERSION = 'v1.0-stable'
ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin15081508')
SELF_URL = os.getenv('SELF_URL', 'https://celestial-qbies-engine.onrender.com/health')
PING_INTERVAL = int(os.getenv('PING_INTERVAL', '300'))
MAX_FAILS = int(os.getenv('MAX_FAILS', '3'))

quantum_state = {'total_energy': 0.0, 'entropy': 0.0}

# -------------------------------
# API Endpoints
# -------------------------------
@app.get('/')
def index():
    return {'engine': 'Celestial QBIES', 'version': CEL_ENGINE_VERSION, 'status': 'running'}

@app.get('/health')
def health():
    uptime = time.time() - start_time
    return {'ok': True, 'status': 'running', 'uptime': f'{uptime:.0f}s'}

@app.get('/uptime')
def uptime():
    return {'uptime_seconds': int(time.time() - start_time)}

@app.get('/status')
def status():
    return {'version': CEL_ENGINE_VERSION, 'quantum_state': quantum_state, 'uptime': int(time.time() - start_time)}

@app.post('/energy')
async def add_energy(request: Request):
    data = await request.json()
    value = float(data.get('value', 0))
    quantum_state['total_energy'] += value
    quantum_state['entropy'] = (quantum_state['entropy'] * 0.9) + (value * 0.1)
    return {'ok': True, 'added': value, 'total_energy': quantum_state['total_energy'], 'entropy': quantum_state['entropy']}

@app.post('/restart')
async def restart(req: Request):
    data = await req.json()
    if data.get('password') == ADMIN_PASS:
        os._exit(0)
    return {'error': 'Unauthorized'}

@app.post('/shutdown')
async def shutdown(req: Request):
    data = await req.json()
    if data.get('password') == ADMIN_PASS:
        os._exit(1)
    return {'error': 'Unauthorized'}

# -------------------------------
# Internal Watchdog (auto-heal)
# -------------------------------
def watchdog():
    fail_count = 0
    while True:
        try:
            res = requests.get(SELF_URL, timeout=10)
            if res.status_code == 200:
                fail_count = 0
                print(f'✅ Health OK — {res.status_code}', flush=True)
            else:
                fail_count += 1
                print(f'⚠️ Health failed — code {res.status_code}, fail {fail_count}/{MAX_FAILS}', flush=True)
        except Exception as e:
            fail_count += 1
            print(f'❌ Exception: {e}, fail {fail_count}/{MAX_FAILS}', flush=True)
        if fail_count >= MAX_FAILS:
            print('🚨 Too many failures — restarting...', flush=True)
            time.sleep(2)
            os._exit(0)
        time.sleep(PING_INTERVAL)

threading.Thread(target=watchdog, daemon=True).start()
print('🧠 Passive Watchdog started (internal, free mode).')
