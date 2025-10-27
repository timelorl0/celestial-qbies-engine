
import json, os, hashlib, time, random
from typing import Dict, Any, List

class QBI:
    def __init__(self, obj: Dict[str, Any], path: str):
        self.obj = obj
        self.path = path
        self.nodes = obj.get("nodes", {})
        self.files = obj.get("files", [])
        self.policy = obj.get("policy", {"replication_factor": 2, "parity":"xor", "parity_group_size":4})

    @staticmethod
    def load(path: str) -> "QBI":
        if not os.path.exists(path):
            obj = {
                "version": "1.1",
                "policy": {"replication_factor": 2, "parity": "xor", "parity_group_size":4, "shard_size":4194304, "hash_algo":"blake3"},
                "files": [],
                "nodes": {}
            }
            return QBI(obj, path)
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        return QBI(obj, path)

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.obj, f, ensure_ascii=False, indent=2)

    def update_node(self, node_id: str, shards: List[Dict[str,Any]], free_mb: int):
        self.nodes[node_id] = {"free_mb": free_mb, "last": int(time.time())}
        self.obj["nodes"] = self.nodes
        self.save()

    def iter_shards(self):
        for f in self.files:
            for sh in f.get("shards", []):
                yield f, sh

    def plan_replication(self, base_dir: str):
        k = self.policy.get("replication_factor", 2)
        actions = []
        node_ids = list(self.nodes.keys())
        # ensure replicas >= k
        for f, sh in self.iter_shards():
            reps = sh.get("replicas", [])
            # if shard not present on server storage but supposed to exist, skip check
            if len(reps) < k and node_ids:
                # choose additional node not already in list
                for nid in node_ids:
                    if nid not in reps and self.nodes[nid].get("free_mb", 0) > 50:
                        reps.append(nid)
                        sh["replicas"] = reps
                        actions.append({"type":"replicate","file":f["name"],"shard_id":sh["id"],"dst":nid})
                        break
        self.save()
        return actions

    def bump_hash(self, file: str, shard_id: int):
        for f in self.files:
            if f["name"] == file:
                for sh in f["shards"]:
                    if sh["id"] == shard_id:
                        sh["hash"] = hashlib.sha256(str(time.time()).encode()).hexdigest()
                        self.save()
                        return
