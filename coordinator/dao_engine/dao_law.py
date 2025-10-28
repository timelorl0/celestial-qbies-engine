
# dao_law.py — Thiên Đạo Luật
from typing import Dict, Any

def evaluate_law(context: Dict[str, Any]) -> Dict[str, Any]:
    # Simple rule sample: if chaos > 70 → apply Heaven Seal (debuff), else gentle blessing
    chaos = context.get("chaos", 0)
    if chaos >= 70:
        return {"type":"seal", "level":"major", "duration_sec": 300, "message":"Thiên Ấn giáng lâm — hỗn loạn bị phong."}
    return {"type":"bless", "level":"minor", "duration_sec": 180, "message":"Đạo vận thuận — nhận ban phúc nhẹ."}
