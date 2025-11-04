# coordinator/modules/willcore.py
"""
WillCore: ý chí/nguyện lực — ảnh hưởng tỉ lệ thành công khi sáng tạo công pháp / đột phá.
"""
WILLS = {}

def init(app=None, config=None):
    print("[WillCore] ready")

def add_will(player, amount):
    WILLS[player] = WILLS.get(player,0) + amount
    return WILLS[player]

def get_will(player):
    return WILLS.get(player, 0)