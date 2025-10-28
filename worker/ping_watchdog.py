"""
ping_watchdog.py
- Ping /health của service mỗi khoảng (mặc định 600s).
- Nếu không trả 200 => gọi Render API để redeploy.
- Dùng biến môi trường: RENDER_API_KEY, RENDER_SERVICE_ID, TARGET_URL (tùy chọn).
"""

import os, time, sys
try:
    import requests
except Exception as e:
    print('requests not installed in this environment; Render will install from requirements.txt')
    # continue; runtime on Render will install requests

RENDER_API_KEY = os.getenv('RENDER_API_KEY')
RENDER_SERVICE_ID = os.getenv('RENDER_SERVICE_ID')
TARGET_URL = os.getenv('TARGET_URL', 'https://celestial-qbies-engine.onrender.com/health')
PING_INTERVAL = int(os.getenv('PING_INTERVAL_SECONDS', '600'))
TIMEOUT = int(os.getenv('PING_TIMEOUT', '10'))

if not RENDER_API_KEY or not RENDER_SERVICE_ID:
    print('ERROR: RENDER_API_KEY or RENDER_SERVICE_ID missing. Exiting.')
    sys.exit(2)

HEADERS = {
    'Authorization': f'Bearer {RENDER_API_KEY}',
    'Content-Type': 'application/json',
}

REDEPLOY_URL = f'https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys'

def trigger_redeploy():
    try:
        r = requests.post(REDEPLOY_URL, headers=HEADERS, json={})
        print('Redeploy response:', r.status_code, r.text[:400])
        return r.status_code in (200,201)
    except Exception as e:
        print('Redeploy failed:', e)
        return False

def ping_health():
    try:
        r = requests.get(TARGET_URL, timeout=TIMEOUT)
        return r.status_code, r.text[:400]
    except Exception as e:
        return None, str(e)

def main():
    print('Watchdog started. Target:', TARGET_URL, 'Interval:', PING_INTERVAL)
    while True:
        code, body = ping_health()
        if code == 200:
            print(time.strftime('%Y-%m-%d %H:%M:%S'), 'OK 200. preview:', body)
        else:
            print(time.strftime('%Y-%m-%d %H:%M:%S'), 'Bad response:', code, body)
            ok = trigger_redeploy()
            print('Redeploy triggered:', ok)
        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main()
