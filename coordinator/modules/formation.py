# coordinator/modules/formation.py
"""
Formation (Trận pháp): đặt trận, kích hoạt, dọn mạch.
"""
ACTIVE = {}

def init(app=None, config=None):
    print("[Formation] ready")

def create_formation(owner, pattern, location):
    fid = f"frm-{int(time.time())}"
    ACTIVE[fid] = {"owner":owner,"pattern":pattern,"location":location,"active":True}
    return {"id":fid}

def dismantle(fid):
    if fid in ACTIVE:
        del ACTIVE[fid]
        return True
    return False