#!/bin/bash
echo "🚀 Kiểm tra route SystemAPI..."
python3 - <<PY
from coordinator.api import system_api
print("✅ Route nạp:", [r.path for r in system_api.router.routes])
PY
echo "⚙️ Hoàn tất. Commit và redeploy Render nhé."

