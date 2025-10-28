#!/usr/bin/env bash
set -e
VER="${1:-1.20.1}"
API="https://api.papermc.io/v2/projects/paper/versions/${VER}"
echo "[*] Fetching latest build for Paper ${VER} ..."
BUILD=$(curl -fsSL "$API" | jq -r '.builds[-1]')
URL="https://api.papermc.io/v2/projects/paper/versions/${VER}/builds/${BUILD}/downloads/paper-${VER}-${BUILD}.jar"
echo "[*] Download: $URL"
curl -fSL "$URL" -o paper.jar
echo "[*] Done. Use ./start.sh"
