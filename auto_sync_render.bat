@echo off
chcp 65001 >nul
echo ==============================================
echo 🌌 Celestial-QBIES Auto Sync & Render Uploader
echo ==============================================

:: Bước 1 - Kiểm tra Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git chưa được cài đặt. Vui lòng cài Git trước.
    pause
    exit /b
)

:: Bước 2 - Lấy code mới nhất từ GitHub
echo 🔄 Đang kéo bản cập nhật từ GitHub...
git pull origin main
if %errorlevel% neq 0 (
    echo ⚠️ Không thể kéo code. Tiếp tục với phiên bản cục bộ...
)

:: Bước 3 - Kiểm tra thay đổi
echo 📦 Kiểm tra thay đổi cục bộ...
git add .
git status

:: Bước 4 - Commit tự động
set /p msg="📝 Nhập nội dung commit (Enter để dùng mặc định): "
if "%msg%"=="" set msg=Auto-sync from local Celestial Engine build
git commit -m "%msg%" >nul 2>&1

:: Bước 5 - Push lên GitHub
echo 🚀 Đang đẩy code lên GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo ❌ Đẩy code thất bại. Kiểm tra kết nối mạng hoặc token GitHub.
    pause
    exit /b
)
echo ✅ Đã đồng bộ GitHub thành công!

:: Bước 6 - Gọi Render tự deploy (nếu có webhook)
set RENDER_HOOK=https://api.render.com/deploy/srv-xxxxxx  REM <--- thay bằng link Deploy Hook trong Render
if not "%RENDER_HOOK%"=="" (
    echo 🔔 Gửi tín hiệu deploy lên Render...
    curl -X POST %RENDER_HOOK%
)

echo ==============================================
echo ✅ Hoàn tất đồng bộ và kích hoạt Render Build!
echo ==============================================
pause