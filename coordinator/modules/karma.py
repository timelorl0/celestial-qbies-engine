# coordinator/modules/karma.py
"""
Karma system: quản lý nghiệp (gán điểm, lưu lịch sử)
"""
HISTORY = {}

def init(app=None, config=None):
    print("[Karma] ready")

def add_karma(player, delta, reason=""):
    rec = HISTORY.setdefault(player, [])
    rec.append({"time":int(time.time()), "delta":delta, "reason":reason})
    total = sum(r["delta"] for r in rec)
    return {"player":player,"karma":total}