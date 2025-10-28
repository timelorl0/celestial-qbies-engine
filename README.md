
# Celestial–QBIES Hybrid Integration Pack

This zip contains everything to run the hybrid setup:
- **Coordinator** (Python FastAPI) to manage QBIES
- **Sample index.qbi + demo shards**
- **Auto-checkpoint** script
- **PaperMC plugins**: Node (client) and Bridge (server)

## Quick Start (Render, free, no credit card)
1. Create a **Web Service** on Render from `coordinator/`.
2. Add a **persistent disk** (1–5GB) mounted at `/data`.
3. Deploy; it serves `uvicorn app:app` via `Procfile`.
4. SSH/Deploy the sample `coordinator/data/qbies` folder to `/data/qbies`.
5. Note the service URL, e.g. `https://your-render-service.onrender.com`.

## Minecraft side
- Put `plugins/qbies-server-bridge` (built JAR) into your **server** (Paper 1.20.x).
- Put `plugins/qbies-node-plugin` (built JAR) into **player clients** or distribute as a required mod/plugin if you control the client.
- In both plugins' `config.yml`, set `COORD_URL` to the Render URL.
- Start server; use `/dao read timeline.qbs 0` to test fetching a fragment.
  You should see `QBIES_FRAGMENT timeline.qbs#0`.

## Checkpoint
Run `python coordinator/checkpoint.py` (on Render shell or locally pointing to `/data/qbies`) to create a `.qbb` bundle in `/data/checkpoints`.
Upload it to Google Drive/GitHub using your preferred method (not included in skeleton).

## Notes
- This is a skeleton for your custom QBIES logic. Encryption/parity are stubbed for clarity.
- Extend `storage.py` to implement real fragment sealing (AES-GCM/ChaCha20) and proper `.qbs` parsing.
- Extend `parity.py` to implement XOR/RS parity repair.
- Extend Node plugin to actually **hold shards** (download via `/fetch`) and **serve deltas** when requested.
