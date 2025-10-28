import os, time, requests

print('🧠 External Watchdog started — cron-job.org expected to ping /health.')

SELF_URL = os.environ.get('SELF_URL', 'https://celestial-qbies-engine.onrender.com/health')
while True:
    try:
        res = requests.get(SELF_URL, timeout=10)
        if res.status_code == 200:
            print('✅ External ping OK')
        else:
            print(f'⚠️ Ping failed: {res.status_code}')
    except Exception as e:
        print(f'❌ External ping exception: {e}')
    time.sleep(300)
