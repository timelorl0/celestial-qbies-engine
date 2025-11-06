@echo off
title 🌌 Celestial Engine Auto Sync Script
color 0B
echo ============================================================
echo   🚀 Celestial Engine Auto Sync - Falix + Render + GitHub
echo ============================================================
echo.

:: === 1. Xác định đường dẫn ===
setlocal
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

:: === 2. Kéo code mới nhất từ GitHub ===
echo [1/4] 🔄 Đang kéo dữ liệu mới nhất từ GitHub...
git fetch origin main >nul 2>&1
git pull origin main
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Lỗi khi kéo dữ liệu từ GitHub. Kiểm tra kết nối.
    pause
    exit /b
)
echo ✅ Đã đồng bộ code từ GitHub.
echo.

:: === 3. Biên dịch QCoreBridge ===
if exist "QCoreBridge" (
    echo [2/4] 🧱 Đang biên dịch QCoreBridge.jar...
    cd "QCoreBridge"
    if exist QCoreBridge.jar del /f QCoreBridge.jar
    if exist build rd /s /q build
    mkdir build

    javac --release 21 -encoding UTF-8 -cp "lib/*" -d build src\qbieslink\*.java src\qbieslink\commands\*.java
    if %errorlevel% neq 0 (
        color 0C
        echo ❌ Lỗi biên dịch Java! Kiểm tra lại mã nguồn.
        pause
        exit /b
    )
    copy plugin.yml build\ >nul
    cd build
    jar cf ..\QCoreBridge.jar .
    cd ..
    echo ✅ Đã build thành công QCoreBridge.jar
    cd ..
) else (
    echo ⚠️ Không tìm thấy thư mục QCoreBridge, bỏ qua build.
)
echo.

:: === 4. Ghi log đồng bộ ===
echo [3/4] 🧾 Ghi log đồng bộ...
git add .
git commit -m "🔁 Auto Sync Commit - %date% %time%" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Không có thay đổi mới để commit.
)
echo.

:: === 5. Đẩy dữ liệu lên GitHub ===
echo [4/4] ☁️ Đang đẩy lên GitHub...
git push origin main
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Lỗi khi push lên GitHub! Kiểm tra kết nối mạng hoặc token.
    pause
    exit /b
)
echo ✅ Thành công! Toàn bộ dự án đã được đẩy lên GitHub.
echo.

:: === 6. Hoàn tất ===
color 0A
echo ============================================================
echo   🌠 Hoàn tất đồng bộ Celestial Engine Universe
echo ============================================================
pause
exit /b