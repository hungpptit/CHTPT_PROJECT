#lớp mạng cho client
# client_net.py
import socket, threading, json, queue
from protocol import send_json

class ClientNetwork(threading.Thread):
    """
    Quản lý kết nối đến server:
     - Gửi REGISTER ngay sau khi connect
     - Đẩy mọi thông điệp nhận được vào inbox (queue) cho GUI xử lý
     - Cung cấp request_cs() / release_cs()
    """
    def __init__(self, host, port, client_id, inbox_queue, on_disconnect):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.client_id = client_id
        self.inbox = inbox_queue
        self.on_disconnect = on_disconnect
        self.sock = None
        self._stop = threading.Event()

    def run(self):
        buffer = ""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            send_json(self.sock, {"type": "REGISTER", "client_id": self.client_id})
            while not self._stop.is_set():
                data = self.sock.recv(4096)
                if not data:
                    break
                buffer += data.decode('utf-8', errors='ignore')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    self.inbox.put(msg)
        except Exception as e:
            self.inbox.put({"type": "LOG", "msg": f"[NET] Error: {e}"})
        finally:
            try:
                if self.sock:
                    self.sock.close()
            except Exception:
                pass
            self.on_disconnect()

    def stop(self):
        self._stop.set()
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass

    def request_cs(self):
        if self.sock:
            send_json(self.sock, {"type": "REQUEST", "client_id": self.client_id})

    def release_cs(self):
        if self.sock:
            send_json(self.sock, {"type": "RELEASE", "client_id": self.client_id})

    # ===================================
    # 🔥 HÀM MỚI: Gửi yêu cầu rút tiền ATM
    # ===================================
    def withdraw(self, amount):
        if self.sock:
            send_json(self.sock, {
                "type": "WITHDRAW",
                "client_id": self.client_id,
                "amount": amount
            })
