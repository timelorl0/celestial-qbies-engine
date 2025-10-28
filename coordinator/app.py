from fastapi import FastAPI, Request
import os, time, threading, requests

app = FastAPI()
start_time = time.time()
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'admin15081508')
SELF_URL = os.environ.get('SELF_URL', 'https://celestial-qbies-engine.onrender.com/health')
PING_INTERVAL = int(os.environ.get('PING_INTERVAL', '300'))
MAX_FAILS = int(os.environ.get('MAX_FAILS', '3'))
fail_count = 0

@app.get('/health')
def health():
    uptime = time.time() - start_time
    return {'ok': True, 'status': 'running', 'uptime': f'{uptime:.0f}s'}

@app.get('/uptime')
def uptime():
    return {'uptime_seconds': int(time.time() - start_time)}

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

def watchdog():
    global fail_count
    while True:
        try:
            res = requests.get(SELF_URL, timeout=10)
            if res.status_code == 200:
                fail_count = 0
                print(f'✅ Health OK — {res.status_code}')
            else:
                fail_count += 1
                print(f'⚠️ Health failed — code {res.status_code}, fail {fail_count}/{MAX_FAILS}')
        except Exception as e:
            fail_count += 1
            print(f'❌ Exception: {e}, fail {fail_count}/{MAX_FAILS}')
        if fail_count >= MAX_FAILS:
            print('🚨 Too many failures — restarting...')
            time.sleep(2)
            os._exit(0)
        time.sleep(PING_INTERVAL)

threading.Thread(target=watchdog, daemon=True).start()
print('🧠 Passive Watchdog started (internal, free mode).')
