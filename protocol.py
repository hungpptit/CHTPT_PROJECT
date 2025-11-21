# tiện ích gửi JSON theo dòng
# protocol.py
import json

def send_json(sock, obj):
    """Gửi 1 thông điệp JSON kết thúc bằng newline (NDJSON)."""
    try:
        data = json.dumps(obj, separators=(',', ':')) + '\n'
        sock.sendall(data.encode('utf-8'))
    except Exception:
        pass  # socket có thể đã đóng
