# ==========================================
# 🌌 Celestial Engine - Thiên Đạo Liên Thông
# Phiên bản: v5.1 – Kết nối Falix <-> Render
# ==========================================
from fastapi import FastAPI, Request
import datetime
import asyncio

# ======================================================
# 🔹 Khởi tạo ứng dụng FastAPI chính cho hệ thống Render
# ======================================================
app = FastAPI(title="Celestial Engine - Thiên Đạo Liên Thông", version="5.1")

# ======================================================
# 🔸 API hệ thống sẵn có (bạn có thể giữ nguyên phần này)
# ======================================================
@app.get("/")
def root():
    return {
        "message": "🌠 Celestial Engine đang hoạt động.",
        "status": "Thiên Đạo Liên Thông sẵn sàng.",
        "version": "5.1"
    }

@app.get("/status")
def status():
    return {"ok": True, "time": datetime.datetime.now().isoformat()}

# ======================================================
# ⚡ API đồng bộ Falix <-> Render (Mới)
# ======================================================
@app.post("/falix_instant_sync")
async def falix_sync(request: Request):
    """
    Endpoint nhận tín hiệu đồng bộ từ Falix Node.
    Khi Falix update plugin hoặc auto-deploy, nó sẽ gửi POST về đây.
    """
    try:
        data = await request.json()
    except Exception:
        data = {}

    event = data.get("event", "unknown")
    message = data.get("message", "")
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("───────────────────────────────────────────────")
    print(f"⚡ [{time}] Nhận tín hiệu Thiên Đạo từ Falix:")
    print(f"🔹 Sự kiện: {event}")
    print(f"🔹 Nội dung: {message}")
    print("───────────────────────────────────────────────")

    # 🚀 (Tuỳ chọn) Thực thi tự động xử lý hoặc phản hồi về Falix ở đây
    await asyncio.sleep(0.1)
    return {"status": "ok", "event": event, "message": message}

# ======================================================
# 🧩 API kiểm tra tức thì (test endpoint)
# ======================================================
@app.get("/test_sync")
def test_sync():
    time = datetime.datetime.now().strftime("%H:%M:%S")
    return {"message": f"✅ Falix-Render Sync OK tại {time}"}

# ======================================================
# 🧬 Chạy trực tiếp (dành cho debug hoặc local test)
# ======================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000, reload=True)