from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# ===============================
# 🌉 QbiesLink Bridge Status API
# ===============================

class BridgeStatus(BaseModel):
    plugin: str = "QCoreBridge"
    node: str = "Unknown"
    status: str = "disconnected"
    info: str = "Chưa nhận tín hiệu"
    players: int = 0
    timestamp: float = datetime.now().timestamp()

# Lưu trạng thái cầu nối hiện tại (toàn cục)
current_bridge_status = BridgeStatus()

@router.post("/bridge_status")
async def update_bridge_status(status: BridgeStatus):
    global current_bridge_status
    current_bridge_status = status
    print(f"[Thiên Đạo] ⚡ Bridge cập nhật: {status.status} ({status.info}) từ {status.node}")
    return {"success": True, "bridge": current_bridge_status}

@router.get("/bridge_status")
async def get_bridge_status():
    return current_bridge_status