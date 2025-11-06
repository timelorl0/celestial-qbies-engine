@echo off
title 🌌 Celestial Engine Auto Sync
color 0B

echo ======================================
echo 🔄  Celestial Engine Auto Sync Script
echo ======================================
echo.

REM --- Kiểm tra Git ---
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git chua duoc cai dat hoac khong ton tai trong PATH.
    pause
    exit /b
)

REM --- Lưu thay đổi nội bộ ---
echo 📦 Luu thay doi hien tai vao Git...
git add .
git commit -m "🌌 Auto-sync local changes"

REM --- Kéo bản mới nhất từ GitHub ---
echo 🚀 Dang keo ban moi tu GitHub...
git pull origin main --rebase

REM --- Biên dịch plugin ---
echo 🧱 Dang build QCoreBridge.jar...
if exist build (rmdir /s /q build)
if exist QCoreBridge.jar (del /q QCoreBridge.jar)
mkdir build

javac --release 21 -encoding UTF-8 -cp "lib/*" -d build (for /r src %%f in (*.java) do @echo %%f)
if errorlevel 1 (
    echo ❌ Loi bien dich! Kiem tra lai ma nguon.
    pause
    exit /b
)

copy plugin.yml build\
cd build
jar cf ../QCoreBridge.jar .
cd ..

echo ✅ Build hoan tat: QCoreBridge.jar da duoc tao moi.
echo.

REM --- Đẩy bản build mới lên GitHub ---
set /p msg="Nhap noi dung commit (hoac Enter de dung mac dinh): "
if "%msg%"=="" set msg=🌠 Auto-built QCoreBridge update

git add QCoreBridge.jar
git commit -m "%msg%"
git push origin main

echo.
echo 🚀 Day thanh cong len GitHub.
echo.

REM --- (Tùy chọn) Gửi bản build lên Render ---
set /p upload="Ban co muon gui len Render ngay bay gio (Y/N)? "
if /I "%upload%"=="Y" (
    echo 🌐 Dang gui QCoreBridge.jar len Render...
    curl -X POST -F "file=@QCoreBridge.jar" https://celestial-qbies-engine.onrender.com/upload_plugin
)

echo ======================================
echo 🌌 Hoan tat dong bo Celestial Engine!
echo ======================================
pause
curl -X POST https://celestial-qbies-engine.onrender.com/auto_reload -H "Content-Type: application/json" -d "{\"secret\":\"celestial-secret\"}"