# Celestial QBIES Engine – Unified Node + Thiên Đạo
from flask import Flask, jsonify, request
from datetime import datetime
import os, random, math, time

# Import các module hiện có
from coordinator.app import app as coordinator_app
from dao.thien_dao import thien_dao

# Tạo Flask app chính
app = Flask(__name__)

# ========== CORE ENGINE META ==========
ENGINE_VERSION = "Celestial Engine v1.5"
ENGINE_STATUS = "stable"
ENGINE_START = datetime.utcnow()

# ========== ROUTES ==========

@app.route("/")
def index():
    """Trang chào mừng"""
    return jsonify({
        "engine": ENGINE_VERSION,
        "status": ENGINE_STATUS,
        "uptime": str(datetime.utcnow() - ENGINE_START),
        "message": "Celestial QBIES Engine online and harmonized with Thiên Đạo."
    })

# ----- Hệ thống năng lượng tổng -----
@app.route("/api/system/total_energy", methods=["GET"])
def total_energy():
    """Tính năng lượng tổng hợp"""
    uptime = str(datetime.utcnow() - ENGINE_START)
    data = {
        "engine": ENGINE_VERSION,
        "status": ENGINE_STATUS,
        "energy_total": round(thien_dao.energy, 3),
        "uptime": uptime,
        "nodes": 1
    }
    return jsonify(data)

# ----- Thiên Đạo (Unified Field) -----
@app.route("/api/system/thien_dao", methods=["GET"])
def get_thien_dao():
    """Trả về hiện trạng Thiên Đạo"""
    return jsonify(thien_dao.manifest())

# ----- Pulse API (nếu cần Node khác kết nối) -----
@app.route("/api/nodes/pulse", methods=["POST"])
def node_pulse():
    """Nhận Pulse từ các Node phụ"""
    data = request.get_json(force=True)
    node = data.get("node")
    energy = data.get("energy")
    status = data.get("status")
    print(f"[Pulse] Node {node} → {status}, Energy={energy}")
    thien_dao.observe([data])  # Cập nhật trạng thái Thiên Đạo
    return jsonify({"result": "ok", "node": node, "energy": energy})

# ========== ENDPOINT TEST ==========
@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Giao diện mini hiển thị trạng thái"""
    uptime = str(datetime.utcnow() - ENGINE_START)
    return f"""
    <pre style='color:lime; background:black; padding:20px;'>
    🌌 {ENGINE_VERSION} – Multi-Node Network
    =========================================
    Status: {ENGINE_STATUS}
    Uptime: {uptime}
    Energy: {round(thien_dao.energy, 4)}
    State : {thien_dao.state}
    Node  : {thien_dao.node_id}
    =========================================
    Pulse URL: /api/nodes/pulse
    Thiên Đạo: /api/system/thien_dao
    </pre>
    """

# ========== MAIN ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"[Celestial Engine] 🚀 Running on port {port}")
    app.run(host="0.0.0.0", port=port)