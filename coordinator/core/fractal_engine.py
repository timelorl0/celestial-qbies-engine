import os, time, threading
from .qbies_core import write_snapshot, read_snapshot

class FractalEngine:
    def __init__(self, cache_dir="cache/snapshots", filename="universe.qbie"):
        self.cache_dir = cache_dir
        self.filename = filename
        self.path = os.path.join(cache_dir, filename)
        os.makedirs(cache_dir, exist_ok=True)
        self.universe = {"meta": {"genesis": time.time()}, "modules": {}}
        self.lock = threading.RLock()
        self.dirty = False
        self.running = False
        self.autosave_interval = 30  # giây

    def load_universe(self):
        if os.path.exists(self.path):
            try:
                self.universe = read_snapshot(self.path)
                print("🌌 [Fractal] Đã nạp snapshot:", self.path)
            except Exception as e:
                print("⚠ Không thể nạp snapshot:", e)
        else:
            print("✨ [Fractal] Bắt đầu vũ trụ mới (GENESIS).")
        self.start_autosave()

    def evolve(self, ctx=None):
        """Tiến hoá fractal (gọi mỗi khi Falix gửi heartbeat)."""
        with self.lock:
            now = time.time()
            meta = self.universe.setdefault("meta", {})
            meta["last_tick"] = now
            mods = self.universe.setdefault("modules", {})
            if ctx and "player" in ctx:
                p = ctx["player"]
                info = mods.setdefault(p, {"visits": 0, "last": 0})
                info["visits"] += 1
                info["last"] = now
            self.dirty = True
            print(f"🧬 [Fractal] Tiến hoá tại {time.strftime('%H:%M:%S')}")

    def save_universe(self):
        with self.lock:
            write_snapshot(self.path, self.universe)
            self.dirty = False
            print("💾 [Fractal] Lưu snapshot thành công.")

    def start_autosave(self):
        if self.running: return
        self.running = True
        def loop():
            while self.running:
                time.sleep(self.autosave_interval)
                if self.dirty:
                    self.save_universe()
        threading.Thread(target=loop, daemon=True).start()

    def stop_autosave(self):
        self.running = False
        self.save_universe()
        print("🛑 [Fractal] Dừng autosave.")

fractal_engine = FractalEngine()