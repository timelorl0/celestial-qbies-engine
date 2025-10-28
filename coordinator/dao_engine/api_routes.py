
# api_routes.py — expose DaoEngine via FastAPI router
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from .dao_law import evaluate_law
from .dao_war import strategic_tick
from .dao_reincarnate import reincarnate
from .dao_timeline import branch
from .dao_history import record, recent
from .dao_cycle import tick, trigger_if_ready
from .dao_memory import read_memory, write_memory
from .dao_faction import info as fac_info, all_factions

router = APIRouter(prefix="/dao", tags=["dao"])

class LawReq(BaseModel):
    chaos:int = 0
class WarReq(BaseModel):
    factionA_power:int = 40
    factionB_power:int = 50
class ReincReq(BaseModel):
    soul_id:str
    karma:int = 0
class BranchReq(BaseModel):
    flavor: Optional[str] = "alpha"
class HistReq(BaseModel):
    who:str
    what:str
class MemWriteReq(BaseModel):
    soul_id:str
    data: Dict[str,Any]

@router.post("/law")
def api_law(req: LawReq):
    return evaluate_law(req.dict())

@router.post("/war")
def api_war(req: WarReq):
    return strategic_tick(req.dict())

@router.post("/reincarnate")
def api_reinc(req: ReincReq):
    res = reincarnate({"karma": req.karma, "soul_id": req.soul_id})
    return res

@router.post("/timeline/branch")
def api_branch(req: BranchReq):
    return branch(req.dict())

@router.post("/history/record")
def api_hist(r: HistReq):
    return record(r.dict())

@router.get("/history/recent")
def api_recent(n:int = 10):
    return recent(n)

@router.post("/cycle/tick")
def api_tick(delta:int = 1):
    return tick(delta)

@router.post("/cycle/trigger")
def api_trigger():
    return trigger_if_ready()

@router.get("/memory/read")
def api_mem_read(soul_id:str):
    return read_memory(soul_id)

@router.post("/memory/write")
def api_mem_write(req: MemWriteReq):
    return write_memory(req.soul_id, req.data)

@router.get("/faction")
def api_faction(name:str):
    return fac_info(name)

@router.get("/faction/all")
def api_factions():
    return all_factions()
