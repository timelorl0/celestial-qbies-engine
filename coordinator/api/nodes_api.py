from fastapi import APIRouter, Request
import datetime

router = APIRouter(prefix="/api/nodes", tags=["NodesAPI"])

# Danh sách node đang hoạt động (lưu tạm trong RAM)
active_nodes = {}

@router.post("/pulse")
async def receive_pulse(request: Request):
    data = await request.json()
    node_id = data.get("node_id", "unknown")
    status = data.get("status", "unknown")
    energy = data.get("energy", 0)
    uptime = data.get("uptime", 0)
    players = data.get("players", 0)

    active_nodes[node_id] = {
        "status": status,
        "energy": energy,
        "uptime": uptime,
        "players": players,
        "last_seen": datetime.datetime.utcnow().isoformat()
    }

    print(f"[Pulse] ✅ Node {node_id} ({status}) | Energy={energy} | Players={players}")
    return {"ack": True, "connected_nodes": len(active_nodes), "nodes": list(active_nodes.keys())}
