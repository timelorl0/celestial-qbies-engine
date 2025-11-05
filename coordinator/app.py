from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json, os, time
from event_bridge import send_to_falix

app = FastAPI(title="Celestial Engine v2.0 – Reactive")

DATA_PATH = "data/players.json"
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_PATH):
    json.dump({}, open(DATA_PATH, "w"))

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

    # Hồi ứng nếu người chơi vừa đột phá
    if changed:
        msg = f"{player} đã đột phá tới {new_realm}!"
        send_to_falix(player, new_realm, msg)

    return JSONResponse({
        "ok": True,
        "player": player,
        "realm": new_realm,
        "energy": info["energy"],
        "timestamp": time.time()
    })