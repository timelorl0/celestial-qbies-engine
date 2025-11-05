from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json, os, time, requests

app = FastAPI(title="Celestial Engine v2.0 – Reactive")

DATA_PATH = "data/players.json"
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_PATH):
    json.dump({}, open(DATA_PATH, "w"))

# Địa chỉ Falix (ngrok hoặc public endpoint)
FALIX_ENDPOINT = "http://localhost:8080/celestial_event"  # Thay nếu cần

@app.post("/process_event")
async def process_event(req: Request):
    data = await req.json()
    player = data.get("player", "Unknown")
    energy = float(data.get("energy", 0.0))

    db = json.load(open(DATA_PATH))
    info = db.get(player, {"energy": 0.0, "realm": "Phàm Nhân"})
    info["energy"] += energy

    realms = ["Phàm Nhân", "Luyện Khí", "Trúc Cơ", "Kết Đan", "Nguyên Anh", "Hóa Thần", "Hợp Đạo"]
    thresholds = [0, 100, 500, 1500, 4000, 8000, 15000]

    new_realm = realms[0]
    for i, t in enumerate(thresholds):
        if info["energy"] >= t:
            new_realm = realms[i]

    changed = (new_realm != info["realm"])
    info["realm"] = new_realm
    db[player] = info
    json.dump(db, open(DATA_PATH, "w"), indent=2, ensure_ascii=False)

    if changed:
        message = f"{player} đã đột phá tới {new_realm}!"
        try:
            requests.post(FALIX_ENDPOINT, json={
                "player": player,
                "realm": new_realm,
                "message": message
            }, timeout=3)
            print(f"↪️ [Thiên Đạo] Phản hồi gửi về Falix: {player} -> {new_realm}")
        except Exception as e:
            print(f"⚠️ Lỗi gửi về Falix: {e}")

    return JSONResponse({
        "ok": True,
        "player": player,
        "realm": new_realm,
        "energy": info["energy"],
        "timestamp": time.time()
    })