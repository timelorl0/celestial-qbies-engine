@echo off
cd /d "%~dp0"
echo ==========================================
echo 🚀 Celestial QBIES Auto Fix + Push Script
echo ==========================================

:: 1️⃣ Dọn dẹp file khóa nếu có
if exist ".git\index.lock" (
    echo 🧹 Xoa file khoa Git cu...
    del /f /q ".git\index.lock"
)

:: 2️⃣ Lưu tạm thay đổi hiện tại
echo 💾 Stash thay doi tam thoi...
git stash

:: 3️⃣ Lấy bản mới nhất từ GitHub
echo 🔄 Fetch + Pull ban moi nhat...
git fetch origin main
git pull origin main --rebase

:: 4️⃣ Tự động giữ lại bản local nếu có conflict
echo ⚙️ Tu dong giai quyet xung dot...
git checkout --ours coordinator/app.py 2>nul
git add coordinator/app.py 2>nul
git rebase --continue 2>nul

:: 5️⃣ Commit thay đổi mới
git add .
git commit -m "Auto fix & sync %date% %time%" >nul 2>&1

:: 6️⃣ Push lên GitHub (ép đồng bộ)
echo ☁️ Day len GitHub (force sync)...
git push origin main --force

:: 7️⃣ Kết thúc
echo ✅ Da dong bo thanh cong voi GitHub!
echo ==========================================
pause