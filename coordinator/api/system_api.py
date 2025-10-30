from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/system", tags=["SystemAPI"])

@router.get("/total_energy")
def total_energy(json: int = 0):
    data = {
        "engine": "Celestial Engine v1.5",
        "status": "stable",
        "energy_total": 1.0,
        "uptime": datetime.utcnow().isoformat(),
        "nodes": 1
    }
    return data if json == 1 else {"detail": "Celestial Engine active."}

