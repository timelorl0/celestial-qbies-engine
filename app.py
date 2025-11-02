# =============================================
#  Celestial QBIES Engine – Render Flask API
#  Phiên bản mở rộng tương thích QCoreBridge
#  Tác giả: Celestial Engine Dev Team
#  Cập nhật: 2025-11-02
# =============================================

from flask import Flask, jsonify, request
from datetime import datetime
import random

app = Flask(__name__)

# =========================================================
# ⚙️ Thông tin hệ thống & heartbeat
# =========================================================
@app.route("/")
def index():
    return jsonify({
        "service": "Celestial-QBIES-Engine",
        "status": "✅ Online",
        "time": datetime.utcnow().isoformat() + "Z"
    })


@app.route("/api/ping")
def ping():
    return jsonify({"pong": True, "time": datetime.utcnow().isoformat()})


# =========================================================
# 🌌 API cấu hình dành cho QCoreBridge (Minecraft Plugin)
# =========================================================
@app.route("/api/config")
def api_config():
    """
    Endpoint chính để QCoreBridge tải cấu hình.
    Plugin sẽ tự động đọc các giá trị này mỗi 30s.
    """

    # Bạn có thể mở rộng các thông số này dễ dàng
    config = {
        "show_particles": True,
        "show_sound": True,
        "realm_particle": "SOUL_FIRE_FLAME",
        "realm_sound": "ENTITY_PLAYER_LEVELUP",
        "realm_name": "Luyện Khí",
        "realm_color": "GOLD",
        "meditation_gain_rate": 1.5,
        "breakthrough_requirement": 100.0,
        "energy_multiplier": 1.0,
        "enable_auto_update": True
    }

    # Tùy chọn: Nếu plugin gửi player info, có thể phản hồi riêng cho người chơi
    player_name = request.args.get("player")
    if player_name:
        config["message"] = f"Xin chào, {player_name}! Linh khí đang cộng hưởng với bạn."
        config["personal_luck"] = round(random.uniform(0.8, 1.2), 3)

    return jsonify(config)


# =========================================================
# 🔮 API mô phỏng năng lượng vũ trụ / Chu Thiên
# =========================================================
@app.route("/api/energy")
def api_energy():
    """
    Trả về năng lượng vũ trụ (dành cho dashboard hoặc game engine khác).
    """
    total_energy = round(random.uniform(80.0, 120.0), 3)
    cosmic_state = random.choice(["Ổn định", "Dao động", "Cộng hưởng", "Bão linh khí"])
    return jsonify({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_energy": total_energy,
        "cosmic_state": cosmic_state
    })


# =========================================================
# 🧩 API phản hồi test dữ liệu (debug tiện lợi)
# =========================================================
@app.route("/api/test")
def api_test():
    """
    Dành cho thử nghiệm nhanh — kiểm tra kết nối từ QCoreBridge.
    """
    q = request.args.get("q", "Không có dữ liệu")
    return jsonify({
        "received": q,
        "status": "ok",
        "time": datetime.utcnow().isoformat()
    })


# =========================================================
# 🚀 Chạy server Flask
# =========================================================
if __name__ == "__main__":
    # Port cố định để plugin Minecraft gọi tới
    app.run(host="0.0.0.0", port=10000)