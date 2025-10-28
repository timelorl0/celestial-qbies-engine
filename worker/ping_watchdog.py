# ping_watchdog.py — passive auto-heal for Render web service
import os, time, requests, sys, traceback

API_KEY = os.environ.get('RENDER_API_KEY')
SERVICE_ID = os.environ.get('RENDER_SERVICE_ID')
TARGET_URL = os.environ.get('TARGET_URL', 'https://celestial-qbies-engine.onrender.com/health')
PING_INTERVAL = int(os.environ.get('PING_INTERVAL', '300'))  # seconds
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '10'))

def log(*a):
    print('[watchdog]', *a, flush=True)

def trigger_redeploy():
    if not API_KEY or not SERVICE_ID:
        log('No RENDER_API_KEY or RENDER_SERVICE_ID — cannot redeploy via API.')
        return False
    url = f'https://api.render.com/v1/services/{SERVICE_ID}/deploys'
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    try:
        r = requests.post(url, headers=headers, timeout=30)
        log('Redeploy request sent — status:', r.status_code, 'body:', r.text[:400])
        return r.status_code in (200,201,202)
    except Exception as e:
        log('Error sending redeploy request:', e)
        return False

def main_loop():
    fail_count = 0
    MAX_FAILS = int(os.environ.get('MAX_FAILS', '3'))
    while True:
        try:
            r = requests.get(TARGET_URL, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                if fail_count != 0:
                    log('Recovered — health OK (200). Reset fail counter.')
                fail_count = 0
                log('Health OK —', TARGET_URL)
            else:
                fail_count += 1
                log('Health check returned', r.status_code, '- fail_count=', fail_count)
        except Exception as e:
            fail_count += 1
            log('Health check exception:', str(e))
            traceback.print_exc()
        # If exceeded threshold, try redeploy
        if fail_count >= MAX_FAILS:
            log('Max failures reached (', fail_count, '). Triggering redeploy...')
            triggered = trigger_redeploy()
            if triggered:
                log('Redeploy triggered successfully; reset fail_count.')
                fail_count = 0
            else:
                log('Redeploy not triggered (missing API/ID or error).')
        time.sleep(PING_INTERVAL)

if __name__ == '__main__':
    log('Starting passive watchdog. TARGET_URL=', TARGET_URL)
    try:
        main_loop()
    except KeyboardInterrupt:
        log('Interrupted, exiting.')
    except Exception:
        log('Unhandled error:')
        traceback.print_exc()
