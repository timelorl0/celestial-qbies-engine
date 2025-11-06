# ================================================================
# 🌌 Celestial Render Auto Updater v2.0
# ------------------------------------------------
# Tự đồng bộ plugin QCoreBridge từ Falix sang Render (Auto-Apply Safe)
# Có kiểm tra phiên bản, tránh vòng lặp cập nhật.
# ================================================================

import os
import time
import shutil
import datetime
import asyncio
import json
import hashlib

# Cấu hình đường dẫn
UPDATE_DIR = "/home/container/plugins/QCoreBridge/updates"
PLUGIN_PATH = "/home/container/plugins/QCoreBridge/QCoreBridge.jar"
VERSION_FILE = "/home/container/plugins/QCoreBridge/version.json"
CHECK_INTERVAL = 10  # giây

# ======================================================
# 🔹 Hàm lấy mã băm MD5 của file để xác định phiên bản
# ======================================================
def get_file_hash(filepath):
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        print(f"⚠️ [RenderUpdater] Không thể tính hash file {filepath}: {e}")
        return None

# ======================================================
# 🔹 Đọc/ghi file version.json để ghi nhớ phiên bản cũ
# ======================================================
def load_version_info():
    if not os.path.exists(VERSION_FILE):
        return {"last_hash": None, "last_update": None}
    try:
        with open(VERSION_FILE, "r") as f:
            return json.load(f)
    except:
        return {"last_hash": None, "last_update": None}

def save_version_info(file_hash):
    data = {
        "last_hash": file_hash,
        "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(VERSION_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ======================================================
# 🔹 Tác vụ nền chính: Theo dõi, so sánh và cập nhật
# ======================================================
async def monitor_updates():
    print("🧩 [RenderUpdater] Bắt đầu theo dõi thư mục:", UPDATE_DIR)

    last_info = load_version_info()
    last_hash = last_info.get("last_hash")

    while True:
        try:
            if not os.path.exists(UPDATE_DIR):
                print(f"⚠️ [RenderUpdater] Thư mục {UPDATE_DIR} không tồn tại, đang tạo...")
                os.makedirs(UPDATE_DIR, exist_ok=True)
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            files = [f for f in os.listdir(UPDATE_DIR) if f.endswith(".jar")]
            if not files:
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            newest = max(files, key=lambda f: os.path.getmtime(os.path.join(UPDATE_DIR, f)))
            file_path = os.path.join(UPDATE_DIR, newest)

            new_hash = get_file_hash(file_path)
            if not new_hash:
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            if new_hash == last_hash:
                # Không có thay đổi
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            print(f"🚀 [RenderUpdater] Phát hiện bản cập nhật mới: {newest}")
            print("📦 [RenderUpdater] Tiến hành ghi đè plugin hiện tại...")

            shutil.copy2(file_path, PLUGIN_PATH)
            save_version_info(new_hash)

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"✅ [{now}] Đã cập nhật QCoreBridge.jar (hash: {new_hash[:12]})")

            # Tái khởi động Render Engine
            print("🔄 [RenderUpdater] Tái khởi động Render Engine để nạp bản mới...")
            os.system("supervisorctl restart all || kill 1")

            # Cập nhật bộ nhớ tạm
            last_hash = new_hash

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"⚠️ [RenderUpdater] Lỗi khi kiểm tra cập nhật: {e}")
            await asyncio.sleep(10)