import time, requests, os

URL = "https://celestial-qbies-engine.onrender.com/health"
RESTART_CMD = "curl -X POST https://api.render.com/v1/services/YOUR_SERVICE_ID/deploys \
-H 'Authorization: Bearer YOUR_API_KEY'"

while True:
    try:
        res = requests.get(URL, timeout=10)
        if res.status_code == 200:
            print("✅ QBIES Engine is alive:", res.json())
        else:
            print("⚠️ Unexpected status:", res.status_code)
            os.system(RESTART_CMD)
    except Exception as e:
        print("❌ Ping failed:", e)
        os.system(RESTART_CMD)
    time.sleep(600)  # 10 phút
