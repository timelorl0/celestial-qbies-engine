
import os, base64, hashlib

def fragment_path(base_dir: str, file: str, shard_id: int) -> str:
    return os.path.join(base_dir, f"{file}.shard{shard_id}")

def shard_exists(base_dir: str, file: str, shard_id: int) -> bool:
    return os.path.exists(fragment_path(base_dir, file, shard_id))

def read_shard(base_dir: str, file: str, shard_id: int) -> bytes:
    p = fragment_path(base_dir, file, shard_id)
    with open(p, "rb") as f:
        return f.read()

def write_shard(base_dir: str, file: str, shard_id: int, data: bytes):
    p = fragment_path(base_dir, file, shard_id)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)

def fetch_fragment_bytes(base_dir: str, file: str, shard_id: int) -> str:
    p = fragment_path(base_dir, file, shard_id)
    if not os.path.exists(p):
        raw = f"QBIES_FRAGMENT {file}#{shard_id}".encode()
    else:
        with open(p, "rb") as f:
            raw = f.read()
    return base64.b64encode(raw).decode()

def apply_delta(base_dir: str, file: str, shard_id: int, patch_b64: str) -> bool:
    blob = base64.b64decode(patch_b64.encode())
    write_shard(base_dir, file, shard_id, blob)
    return True
