
# Celestial–QBIES Universe Pack (Full + Self-Healing)

What's new:
- **Full spec** in `SPEC.md`
- Coordinator v1.1 with:
  - Heartbeat, replication planner
  - Verify endpoint
  - **XOR parity repair**: `/parity/plan` + `/parity/execute`
- Demo `.qbi` with **parity group** and 5 shards (4 data + 1 parity)
- Demo shards created; you can delete one shard file and call parity repair to rebuild.

## Quick Test (locally)
```
cd coordinator
pip install -r requirements.txt
QBIES_DATA=./data/qbies uvicorn app:app --reload
```
- Delete one data shard: `rm data/qbies/timeline.qbs.shard2`
- Plan repair: `POST /parity/plan?file=timeline.qbs&parity_group=pg1`
- Execute:   `POST /parity/execute?file=timeline.qbs&parity_group=pg1`
- Verify it recreated `timeline.qbs.shard2`.

## Deploy (Render, free, no VISA)
- Create Web Service from `coordinator/`, mount disk `/data`
- Ensure `/data/qbies` contains `index.qbi` + `.shard*` files
- Nodes (plugins) send `/heartbeat` to keep dyno awake

## Minecraft integration
- Use the included `mc-server` and `plugins/*` (build with Maven) as in previous README.
- Command `/dao read timeline.qbs 0` fetches a fragment from Coordinator.
