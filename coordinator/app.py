from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json, os, time

app = FastAPI(title="Celestial Engine v1.1 – Instant Mode")

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

    info["realm"] = new_realm
    db[player] = info
    json.dump(db, open(DATA_PATH, "w"), indent=2, ensure_ascii=False)

    print(f"[Thiên Đạo] {player} đạt {new_realm} (năng lượng: {info['energy']:.1f})")

    return JSONResponse({
        "ok": True,
        "player": player,
        "realm": new_realm,
        "energy": info["energy"],
        "timestamp": time.time()
    })