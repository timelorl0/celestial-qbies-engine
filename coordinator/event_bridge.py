import json, requests

FALIX_ENDPOINT = "https://<địa-chỉ-sever-falix-của-bạn-hoặc-ngrok>/celestial_event"

def send_to_falix(player: str, realm: str, msg: str):
    """Gửi thông điệp chủ động từ Thiên Đạo về Falix"""
    try:
        payload = {"player": player, "realm": realm, "message": msg}
        res = requests.post(FALIX_ENDPOINT, json=payload, timeout=3)
        print(f"↪️ [Thiên Đạo] Gửi phản hồi về Falix: {res.status_code}")
    except Exception as e:
        print(f"⚠️ Lỗi gửi về Falix: {e}")