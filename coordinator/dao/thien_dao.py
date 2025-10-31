from datetime import datetime
import random, math

class ThienDao:
    def __init__(self):
        self.energy = 1.0
        self.state = "dormant"
        self.last_pulse = None

    def observe(self, nodes):
        # Quan sát toàn bộ nodes và điều chỉnh entropy
        active = len([n for n in nodes if n.get("status") == "online"])
        if active > 0:
            self.state = "resonating"
            self.energy = 1.0 + math.log1p(active)
        else:
            self.state = "silent"
            self.energy *= 0.99
        self.last_pulse = datetime.utcnow()

    def manifest(self):
        return {
            "manifestation": "Thiên Đạo Hiển Hiện",
            "state": self.state,
            "energy_field": round(self.energy, 4),
            "last_pulse": self.last_pulse
        }

thien_dao = ThienDao()