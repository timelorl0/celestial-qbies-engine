import os, subprocess
from flask import Blueprint, request, jsonify

auto_patch = Blueprint("auto_patch", __name__)

# ⚙️ Đường dẫn tuyệt đối đến thư mục QCoreBridge của bạn
QCORE_PATH = r"C:\QCoreBridge\Thư mục mới\QCoreBridge"

@auto_patch.route("/auto_patch", methods=["POST"])
def patch_plugin():
    """
    API tự vá plugin QCoreBridge và reload ngay trên server Minecraft.
    """
    data = request.get_json(force=True)
    filename = data.get("filename")
    code = data.get("code")

    if not filename or not code:
        return jsonify({"status": "error", "message": "Thiếu filename hoặc code"}), 400

    try:
        # 1️⃣ Ghi đè mã nguồn mới vào file
        file_path = os.path.join(QCORE_PATH, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        # 2️⃣ Biên dịch lại QCoreBridge.jar
        build_cmd = (
            f'cd "{QCORE_PATH}" && '
            'rm -rf build QCoreBridge.jar && mkdir -p build && '
            'javac --release 21 -encoding UTF-8 -cp "lib/*" -d build $(find src -name "*.java") && '
            'cp plugin.yml build/ && (cd build && jar cf ../QCoreBridge.jar .)'
        )
        subprocess.run(build_cmd, shell=True, check=True)

        # 3️⃣ Reload plugin qua RCON (PlugMan)
        # ⚠️ Bạn cần đảm bảo RCON đang bật trong server.properties
        rcon_cmd = 'curl -X POST http://localhost:25575/command -d "plugman reload QCoreBridge"'
        subprocess.run(rcon_cmd, shell=True)

        return jsonify({"status": "success", "message": "✅ Thiên Đạo đã vá và reload QCoreBridge thành công."})

    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": f"Lỗi build: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500