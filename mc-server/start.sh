#!/usr/bin/env bash
set -e
JAR=${1:-paper.jar}
JAVA_OPTS="${JAVA_OPTS:--Xms1G -Xmx2G}"
echo "[*] Starting Paper with ${JAR}"
exec java ${JAVA_OPTS} -jar "${JAR}" nogui
