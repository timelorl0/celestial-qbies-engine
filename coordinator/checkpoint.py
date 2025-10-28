
import tarfile, time, os
from pathlib import Path

DATA = Path(os.environ.get("QBIES_DATA", "/data/qbies"))
OUT = DATA.parent / "checkpoints"
OUT.mkdir(parents=True, exist_ok=True)

def make_qbb():
    ts = int(time.time())
    fname = OUT / f"qbies_cycle_{ts}.qbb"
    with tarfile.open(fname, "w:gz") as tar:
        for p in DATA.glob("*.qbs*"):
            tar.add(p, arcname=p.name)
        if (DATA / "index.qbi").exists():
            tar.add(DATA / "index.qbi", arcname="index.qbi")
    print(f"[checkpoint] Created: {fname}")
    return str(fname)

if __name__ == "__main__":
    make_qbb()
