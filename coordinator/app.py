
from fastapi import FastAPI, Body, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from .qbies_index import QBI
from .storage import fetch_fragment_bytes, apply_delta, read_shard, write_shard, shard_exists
from .parity import plan_repair_xor, xor_repair_execute
import os, time, hashlib

app = FastAPI(title="QBIES Coordinator", version="1.1")

DATA_DIR = os.environ.get("QBIES_DATA", "/data/qbies")
INDEX_FILE = os.path.join(DATA_DIR, "index.qbi")
qbi = QBI.load(INDEX_FILE)

class Heartbeat(BaseModel):
    node_id: str
    shards: List[Dict[str, Any]] = []
    free_mb: int

@app.get("/health")
def health():
    return {"ok": True, "version": "1.1", "time": int(time.time())}

@app.post("/heartbeat")
def heartbeat(hb: Heartbeat):
    qbi.update_node(hb.node_id, hb.shards, hb.free_mb)
    actions = qbi.plan_replication(DATA_DIR)
    return {"ok": True, "actions": actions}

@app.get("/fetch")
def fetch(file: str, shard_id: int):
    blob = fetch_fragment_bytes(DATA_DIR, file, shard_id)
    return {"ok": True, "file": file, "shard_id": shard_id, "data_b64": blob}

class DeltaReq(BaseModel):
    patch_b64: str
    primary: bool = True

@app.post("/delta")
def delta(file: str, shard_id: int, body: DeltaReq):
    ok = apply_delta(DATA_DIR, file, shard_id, body.patch_b64)
    if ok:
        qbi.bump_hash(file, shard_id)
    return {"ok": ok}

@app.post("/verify")
def verify(file: str, shard_id: int):
    # naive: hash the shard on server storage (if present) and return value
    path = os.path.join(DATA_DIR, f"{file}.shard{shard_id}")
    if not os.path.exists(path):
        return {"ok": False, "present": False}
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    return {"ok": True, "present": True, "sha256": h}

@app.post("/parity/plan")
def parity_plan(file: str, parity_group: str):
    plan = plan_repair_xor(qbi, file, parity_group, DATA_DIR)
    return {"ok": True, "plan": plan}

@app.post("/parity/execute")
def parity_execute(file: str, parity_group: str):
    plan = plan_repair_xor(qbi, file, parity_group, DATA_DIR)
    res = xor_repair_execute(plan, DATA_DIR)
    # after rebuild, bump shard hash in index
    for item in res.get("rebuilt", []):
        qbi.bump_hash(file, item["shard_id"])
    return {"ok": True, "result": res}


# Mount DaoEngine routes
from dao_engine.api_routes import router as dao_router
app.include_router(dao_router)
