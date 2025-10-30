#!/bin/bash
echo "🚀 Đang khởi tạo SystemAPI Celestial Engine..."
python3 - <<PY
from coordinator.api import system_api
print("✅ Kiểm tra route:", system_api.router.routes[0].path)
PY
echo "Hoàn tất — hãy commit và deploy lại để kích hoạt API."

