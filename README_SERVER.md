# Celestial–QBIES Server Pack (Hybrid, free, no-VISA)

This pack merges **Coordinator** + a ready-to-fill **PaperMC server**.

## What you need installed
- Java 17+ (for PaperMC & plugins)
- Maven (to build plugins)
- `curl` + `jq` (to download Paper automatically) — or use the PowerShell script on Windows.

## Steps
1) Deploy Coordinator (Render free):
   - Create a Web Service from `coordinator/`
   - Add persistent disk at `/data`
   - Upload `coordinator/data/qbies` to `/data/qbies`
   - Get your service URL, e.g. `https://your-render-service.onrender.com`

2) Build plugins and link to Coordinator:
   - Edit both `plugins/*/src/main/resources/config.yml` → set `COORD_URL` to your Render URL.
   - Run: `./scripts/build_plugins.sh`

3) Prepare PaperMC server:
   - `cd mc-server`
   - **Linux/macOS:** `./setup_paper.sh 1.20.1`  (downloads `paper.jar`)
   - **Windows:** run `powershell.exe -ExecutionPolicy Bypass -File setup_paper.ps1`
   - Confirm `paper.jar` exists.

4) Start server:
   - Accept EULA already set in `eula.txt`
   - **Linux/macOS:** `./start.sh`
   - **Windows:** `start.bat`

5) Test QBIES:
   - Join the server, run: `/dao read timeline.qbs 0`
   - Expected: a message with `QBIES_FRAGMENT timeline.qbs#0`

## Notes
- The Coordinator skeleton serves minimal data & delta APIs; extend encryption/parity as needed.
- Node plugin currently sends heartbeats; you can extend it to actually **hold shards** and serve deltas.
- Use `coordinator/checkpoint.py` to create `.qbb` then upload to your cloud storage.

Enjoy building your living universe. 🌌
