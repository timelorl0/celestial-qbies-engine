
# dao_timeline.py — Timeline song song
from typing import Dict, Any
import random

def branch(info: Dict[str, Any]) -> Dict[str, Any]:
    # Create a new branch id (demo) and a flavor
    branch_id = f"TL-{random.randint(1000,9999)}"
    flavor = info.get("flavor", "alpha")
    return {"branch_id": branch_id, "flavor": flavor, "message": f"Tạo nhánh thời gian {branch_id} ({flavor})."}
