# falix_sync_endpoint.py
from fastapi import FastAPI, Request
import datetime

app = FastAPI(title="Celestial Engine Sync Bridge")

@app.post("/falix_instant_sync")
async def falix_sync(request: Request):
    data = await request.json()
    event = data.get("event", "unknown")
    message = data.get("message", "")
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("──────────────────────────────")
    print(f"⚡ [{time}] Nhận tín hiệu từ Falix:")
    print(f"🔹 Sự kiện: {event}")
    print(f"🔹 Nội dung: {message}")
    print("──────────────────────────────")

    # Ở đây bạn có thể bổ sung:
    # - Ghi log ra file
    # - Kích hoạt render động
    # - Đồng bộ AI hoặc vũ trụ mô phỏng
    return {"status": "ok", "from": "Falix", "event": event, "message": message}

@app.get("/")
def root():
    return {"message": "Celestial Engine đang hoạt động. Thiên Đạo sẵn sàng."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)