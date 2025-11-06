# coordinator/falix_keeper.py
import os, time, threading, requests, traceback

# ================================
# ⚙️ Cấu hình
# ================================
FALIX_SERVER_ID = os.getenv("FALIX_SERVER_ID", "2332736")  # <== thay bằng ID server Falix của bạn
FALIX_BASE = "https://client.falixnodes.net"
FALIX_TIMER_URL = f"{FALIX_BASE}/timer?id={FALIX_SERVER_ID}"
FALIX_START_URL = f"{FALIX_BASE}/server/start?id={FALIX_SERVER_ID}"
FALIX_STATUS_URL = f"{FALIX_BASE}/server/status?id={FALIX_SERVER_ID}"

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", None)
INTERVAL = int(os.getenv("FALIX_KEEP_INTERVAL", "300"))  # 5 phút

# ================================
# 🔔 Gửi thông báo Discord
# ================================
def discord_notify(msg: str):
    if not DISCORD_WEBHOOK:
        print(f"[Falix Keeper] {msg}")
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": f"🛰️ {msg}"}, timeout=10)
    except Exception:
        print(f"[Falix Keeper] Discord send fail: {traceback.format_exc()}")

# ================================
# 💡 Hàm kiểm tra trạng thái
# ================================
def check_status():
    try:
        r = requests.get(FALIX_STATUS_URL, timeout=15)
        if r.status_code == 200 and "online" in r.text.lower():
            return "ONLINE"
        elif "offline" in r.text.lower():
            return "OFFLINE"
        else:
            return "UNKNOWN"
    except Exception:
        return "ERROR"

# ================================
# ⚙️ Gia hạn thời gian Falix
# ================================
def renew_timer():
    try:
        r = requests.get(FALIX_TIMER_URL, timeout=15)
        if r.status_code == 200:
            print(f"[Falix Keeper] Timer renewed OK ✅ ({r.status_code})")
            return True
        else:
            print(f"[Falix Keeper] Timer renew fail ❌ ({r.status_code})")
            return False
    except Exception as e:
        print(f"[Falix Keeper] Renew error: {e}")
        return False

# ================================
# 🚀 Bật lại máy chủ Falix
# ================================
def start_server():
    try:
        r = requests.get(FALIX_START_URL, timeout=15)
        if r.status_code == 200:
            discord_notify("Falix Node đang khởi động lại 🔁")
            print("[Falix Keeper] Falix Node starting...")
            return True
        else:
            discord_notify(f"⚠️ Falix Start thất bại: {r.status_code}")
            print(f"[Falix Keeper] Start failed: {r.status_code}")
            return False
    except Exception as e:
        discord_notify(f"❌ Lỗi khi gửi yêu cầu start: {e}")
        print(f"[Falix Keeper] Start exception: {e}")
        return False

# ================================
# ♻️ Vòng lặp chính
# ================================
def keeper_loop():
    discord_notify("Falix Keeper bắt đầu giám sát 🌐")
    while True:
        try:
            status = check_status()
            print(f"[Falix Keeper] Status: {status}")
            if status == "ONLINE":
                renew_timer()
            elif status == "OFFLINE":
                discord_notify("⚠️ Falix Node đã offline – đang khởi động lại...")
                start_server()
            elif status == "ERROR":
                discord_notify("⚠️ Không thể kết nối tới Falix Node!")
            else:
                print("[Falix Keeper] Trạng thái không xác định.")

        except Exception as e:
            print(f"[Falix Keeper] Loop exception: {e}")
        time.sleep(INTERVAL)

# ================================
# 🧠 Hàm khởi động
# ================================
def start_keeper():
    threading.Thread(target=keeper_loop, daemon=True).start()
    print("[Falix Keeper] Watchdog started.")