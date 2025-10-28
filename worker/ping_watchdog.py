import os, time, sys, requests

print('🧠 Passive Watchdog started (no API key mode). Using cron-job.org expected to ping /health endpoint.')

SELF_URL = os.environ.get('SELF_URL', 'https://celestial-qbies-engine.onrender.com/health')
INTERVAL = int(os.environ.get('PING_INTERVAL', '300'))
MAX_FAILS = int(os.environ.get('MAX_FAILS', '3'))

fail_count = 0
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

    time.sleep(INTERVAL)
