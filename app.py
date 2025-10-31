# ===========================
#  Celestial Engine – app.py
#  Phiên bản 1.5 – Có Thiên Đạo
# ===========================

from fastapi import FastAPI
from dao.thien_dao import thien_dao
from coordinator.app import app as coordinator_app

app = FastAPI(title="Celestial Engine Core", version="1.5")

# Mount app con (coordinator)
app.mount("/coordinator", coordinator_app)


# ----------------------------
# 🧠 Route gốc kiểm tra trạng thái Engine
# ----------------------------
@app.get("/")
def root():
    return {
        "engine": "Celestial Engine v1.5",
        "status": "stable",
        "message": "🌌 Celestial Core online – awaiting resonance..."
    }


# ----------------------------
# ☯️ Route Thiên Đạo
# ----------------------------
@app.get("/api/system/thien_dao")
def get_thien_dao():
    # Nếu có danh sách node hoặc biến trung tâm, truyền vào đây
    try:
        from coordinator.node_manager import NODE_LIST
        thien_dao.observe(NODE_LIST)
    except Exception:
        # fallback nếu không có NODE_LIST
        thien_dao.observe([])

    return thien_dao.manifest()


# ----------------------------
# ⚙️ Route hệ thống năng lượng tổng
# ----------------------------
@app.get("/api/system/total_energy")
def get_total_energy():
    try:
        from coordinator.node_manager import NODE_LIST
        total_nodes = len(NODE_LIST)
    except Exception:
        total_nodes = 0

    return {
        "engine": "Celestial Engine v1.5",
        "status": "stable",
        "energy_total": 1.0,
        "uptime": "active",
        "nodes": total_nodes
    }