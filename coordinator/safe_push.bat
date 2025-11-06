@echo off
cd /d "%~dp0"
echo === Auto Safe Push Celestial Engine ===
git fetch origin main
git pull origin main --rebase
git add .
git commit -m "Auto update %date% %time%"
git push origin main
pause