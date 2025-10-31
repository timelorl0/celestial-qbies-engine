from datetime import datetime
import time, threading, requests, socket, random, math

class ThienDao:
    def __init__(self):
        self.state = "dormant"
        self.energy = 1.0
        self.last_pulse = None
        self.node_id = f"render-{socket.gethostname()}"
        self.engine_url = "https://celestial-qbies-engine.onrender.com/api/nodes/pulse"
        self.active = True

        # Bắt đầu tự động vận hành Thiên Đạo
        self.start_auto_pulse()

    def observe(self, nodes):
        """Quan sát các node khác và điều chỉnh năng lượng Thiên Đạo"""
        active = len([n for n in nodes if n.get("status") == "online"])
        if active > 0:
            self.state = "harmonized"
            self.energy = 1.0 + math.log1p(active)
        else:
            self.state = "silent"
            self.energy = 1.0
        self.last_pulse = datetime.utcnow()

    def manifest(self):
        """Hiển hiện Thiên Đạo – trả về dữ liệu hiện trạng"""
        return {
            "manifestation": "Thiên Đạo Hiển Hiện",
            "state": self.state,
            "energy_field": round(self.energy, 4),
            "last_pulse": self.last_pulse,
            "node_id": self.node_id,
        }

    def send_pulse(self):
        """Gửi một nhịp 'Pulse' về Engine"""
        try:
            payload = {
                "node": self.node_id,
                "status": "online",
                "energy": self.energy,
                "state": self.state,
            }
            res = requests.post(self.engine_url, json=payload, timeout=10)
            print(f"[Thiên Đạo] 🌌 Pulse {self.node_id} → {res.status_code}")
            self.last_pulse = datetime.utcnow()
        except Exception as e:
            print(f"[Thiên Đạo] ⚠️ Lỗi gửi pulse: {e}")

    def start_auto_pulse(self):
        """Khởi chạy luồng tự động gửi pulse định kỳ"""
        def loop():
            while self.active:
                self.send_pulse()
                time.sleep(15 + random.uniform(-3, 3))  # dao động nhịp tự nhiên ±3s
        threading.Thread(target=loop, daemon=True).start()


# Khởi tạo Thiên Đạo toàn cục
thien_dao = ThienDao()