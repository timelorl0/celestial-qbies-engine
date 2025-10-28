
from typing import Dict, Any, List
import os
from .storage import read_shard, write_shard, shard_exists, fragment_path

def plan_repair_xor(qbi, file: str, parity_group: str, base_dir: str) -> Dict[str, Any]:
    # find file entry
    fe = None
    for f in qbi.files:
        if f["name"] == file:
            fe = f
            break
    if not fe: return {"file": file, "parity_group": parity_group, "reason":"file_not_found", "todo":[]}
    # collect members and parity shard
    members = []
    pshard = None
    for sh in fe.get("shards", []):
        if sh.get("parity_group") == parity_group:
            if sh.get("is_parity"):
                pshard = sh["id"]
            else:
                members.append(sh["id"])
    if pshard is None or not members:
        return {"file": file, "parity_group": parity_group, "reason":"no_group", "todo":[]}
    # check which shards exist locally on server storage
    missing = [sid for sid in members if not shard_exists(base_dir, file, sid)]
    plan = {"file":file, "parity_group": parity_group, "parity_id": pshard, "members": members, "missing": missing, "todo":[]}
    # XOR repair only if exactly one missing
    if len(missing) == 1 and shard_exists(base_dir, file, pshard):
        plan["todo"].append({"action":"xor_rebuild","target": missing[0]})
    return plan

def xor_repair_execute(plan: Dict[str, Any], base_dir: str) -> Dict[str, Any]:
    rebuilt = []
    if not plan.get("todo"):
        return {"rebuilt": rebuilt, "note":"nothing_to_do"}
    file = plan["file"]
    target = plan["todo"][0]["target"]
    p_id = plan["parity_id"]
    # read parity
    parity = read_shard(base_dir, file, p_id)
    # XOR with all other member shards (present) to reconstruct missing
    from functools import reduce
    import operator
    acc = bytearray(parity)
    for sid in plan["members"]:
        if sid == target: continue
        pth = fragment_path(base_dir, file, sid)
        if os.path.exists(pth):
            dat = read_shard(base_dir, file, sid)
            # pad shorter to longest
            L = max(len(acc), len(dat))
            if len(acc) < L: acc.extend(b"\x00"*(L-len(acc)))
            if len(dat) < L: dat += b"\x00"*(L-len(dat))
            acc = bytearray([a ^ b for a,b in zip(acc, dat)])
        else:
            # if another member is also missing, cannot rebuild
            return {"rebuilt": rebuilt, "error":"multiple_missing"}
    write_shard(base_dir, file, target, bytes(acc))
    rebuilt.append({"shard_id": target})
    return {"rebuilt": rebuilt}
