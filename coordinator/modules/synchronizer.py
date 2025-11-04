# coordinator/modules/synchronizer.py
"""
Synchronizer: worker đồng bộ giữa Celestial Engine và Minecraft plugin (HTTP).
- Poll endpoint /plugin/ping để xem plugin còn alive.
- Khi patch queue có file, gọi core bridge apply... (stub).
"""
import threading, time, requests

SYNC = {"last_ping":0, "plugin_alive":False, "base_url":"http://localhost:8000"}

def init(app=None, config=None):
    if app and hasattr(app, "extra"):
        # optionally read config
        pass
    print("[Synchronizer] starting background worker")
    t = threading.Thread(target=worker, daemon=True)
    t.start()

def worker():
    while True:
        try:
            r = requests.get(SYNC["base_url"]+"/plugin/ping", timeout=2)
            SYNC["plugin_alive"] = (r.status_code == 200)
            SYNC["last_ping"] = time.time()
        except:
            SYNC["plugin_alive"] = False
        time.sleep(8)