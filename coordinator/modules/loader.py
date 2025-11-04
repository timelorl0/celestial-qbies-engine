# coordinator/modules/loader.py
"""
Module loader: import và init tất cả module Celestial.
Gọi loader.init(app, config) từ app.py để khởi động.
"""
import os
from . import core_bridge, qbies_kernel, attributes, karma, willcore, knowledge_map
from . import alchemy, forge, talisman, formation, synchronizer

MODULES = [
    attributes, karma, willcore, knowledge_map,
    alchemy, forge, talisman, formation,
    core_bridge, synchronizer, qbies_kernel
]

def init(app, config=None):
    """
    Khởi tạo các module theo thứ tự cần thiết.
    app: FastAPI app instance (hoặc None nếu bạn dùng CLI).
    config: dict tùy chỉnh.
    """
    cfg = config or {}
    base = cfg.get("base_path", os.getcwd())
    print("[Loader] Initializing Celestial modules... base=", base)
    for m in MODULES:
        try:
            if hasattr(m, "init"):
                m.init(app=app, config=cfg)
            print(f"[Loader] {m.__name__} initialized")
        except Exception as e:
            print(f"[Loader] ERROR initializing {m.__name__}: {e}")
    print("[Loader] All modules initialized.")