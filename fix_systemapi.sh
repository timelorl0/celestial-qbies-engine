#!/bin/bash
echo "🔧 Kiểm tra SystemAPI..."
python3 - <<PY
from coordinator.api import system_api
print("✅ Route:", [r.path for r in system_api.router.routes])
PY
echo "Hoàn tất — commit & redeploy nhé."

