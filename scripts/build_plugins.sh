#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.."; pwd)"
echo "[*] Building QBIES Node plugin..."
(cd "$ROOT/plugins/qbies-node-plugin" && mvn -q -e -DskipTests package)
echo "[*] Building QBIES Server Bridge plugin..."
(cd "$ROOT/plugins/qbies-server-bridge" && mvn -q -e -DskipTests package)
echo "[*] Copying JARs to mc-server/plugins ..."
cp "$ROOT/plugins/qbies-node-plugin/target/"*.jar "$ROOT/mc-server/plugins/"
cp "$ROOT/plugins/qbies-server-bridge/target/"*.jar "$ROOT/mc-server/plugins/"
echo "[*] Done."
