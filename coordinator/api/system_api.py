# coordinator/api/system_api.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time
from datetime import datetime

# Import Thiên Đạo module
from coordinator.dao.thien_dao import thien_dao

router = APIRouter()

# =============== SYSTEM STATUS ===============
@router.get("/api/system/status")
async def system_status():
    """Trạng thái tổng thể của Celestial Engine"""
    uptime = 0.0
    if thien_dao.last_pulse:
        uptime = round(time.time() - thien_dao.last_pulse.timestamp(), 2)

    last_pulse_str = (
        thien_dao.last_pulse.isoformat() + "Z"
        if thien_dao.last_pulse
        else "No pulse yet"
    )

    return JSONResponse({
        "system": "Celestial Engine v1.5",
        "manifestation": "Thiên Đạo Đang Hiện Hữu",
        "uptime_since_last_pulse": f"{uptime}s",
        "thien_dao_state": thien_dao.state,
        "energy_field": round(thien_dao.energy, 4),
        "last_pulse": last_pulse_str,
    })


# =============== THIÊN ĐẠO CORE ENDPOINT ===============
@router.get("/api/system/thien_dao")
async def get_thien_dao():
    """
    Hiển thị hiện trạng Thiên Đạo (Thiên khí – trạng thái – năng lượng)
    """
    data = thien_dao.manifest()

    # ✅ Chuyển datetime sang chuỗi an toàn cho JSON
    if isinstance(data.get("last_pulse"), datetime):
        data["last_pulse"] = data["last_pulse"].isoformat() + "Z"

    return JSONResponse(data)


# =============== SIMULATION ENDPOINT (TEST) ===============
@router.get("/api/system/simulate_pulse")
async def simulate_pulse(active_nodes: int = 5):
    """
    Dùng để giả lập hoạt động Thiên Đạo trong môi trường Render
    """
    dummy_nodes = [{"status": "online"} for _ in range(active_nodes)]
    thien_dao.observe(dummy_nodes)

    data = thien_dao.manifest()
    if isinstance(data.get("last_pulse"), datetime):
        data["last_pulse"] = data["last_pulse"].isoformat() + "Z"

    return JSONResponse({
        "result": "Pulse simulated successfully.",
        "manifest": data
    })