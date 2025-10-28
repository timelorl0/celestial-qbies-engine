
# Celestial–QBIES FULL Universe Pack (with DaoEngine + Self-Healing)

## New in this pack
- `coordinator/dao_engine/` implementing:
  - 📜 Law (`/dao/law`)
  - ⚔️ War (`/dao/war`)
  - 🕊️ Reincarnation (`/dao/reincarnate`)
  - 🕰️ Timeline (`/dao/timeline/branch`)
  - 🌿 History (`/dao/history/*`)
  - 🪐 Cycle (`/dao/cycle/*`)
  - 🧬 Memory (`/dao/memory/*`)
  - 🏯 Faction (`/dao/faction*`)
- Mounted routes in `coordinator/app.py`
- Updated server plugin commands:
  - `/dao read <file> <shardId>`
  - `/dao reincarnate`
  - `/dao law`
  - `/dao timeline`

## Run locally (Coordinator)
```
cd coordinator
pip install -r requirements.txt
QBIES_DATA=./data/qbies uvicorn app:app --reload
```

## Test in Minecraft (Paper server)
- Build plugins (see previous README), drop jar into `mc-server/plugins`.
- Join and try:
  - `/dao law`
  - `/dao reincarnate`
  - `/dao timeline`

> This is a **working foundation**. Replace demo logic with your real rules and link to true QBIES read/write for souls, timeline, etc.
