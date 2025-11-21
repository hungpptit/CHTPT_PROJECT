# logic tập trung (FIFO)
import threading, time
from protocol import send_json
from collections import deque
import sys

class Coordinator:
    """
    Điều phối tập trung cho ATM:
    - gửi GRANT kèm balance + atm_balance
    """

    def __init__(self, clients_map, balances, get_atm_total, print_lock=None, lease_secs=None):
        self.lock = threading.Lock()
        self.in_cs = None
        self.in_cs_since = 0.0
        self.queue = deque()
        self.clients = clients_map

        self.balances = balances           # ⭐ Số dư từng tài khoản
        self.get_atm_total = get_atm_total # ⭐ Hàm lấy tổng tiền ATM

        self._p_lock = print_lock or threading.Lock()
        self.lease_secs = lease_secs

    def _log(self, *args):
        with self._p_lock:
            print(*args)
            sys.stdout.flush()

    def _send_grant(self, client_id):
        """Gửi GRANT kèm thông tin số dư."""
        sock = self.clients.get(client_id)
        if sock:
            send_json(sock, {
                "type": "GRANT",
                "balance": self.balances.get(client_id, 0),
                "atm_balance": self.get_atm_total()
            })
            self._log(f"[COORD] GRANT -> {client_id}")

    def request_cs(self, client_id):
        with self.lock:
            if self.in_cs == client_id or client_id in self.queue:
                return

            if self.in_cs is None:
                self.in_cs = client_id
                self.in_cs_since = time.time()
                self._send_grant(client_id)

            else:
                self.queue.append(client_id)
                pos = len(self.queue)
                sock = self.clients.get(client_id)

                if sock:
                    send_json(sock, {"type": "QUEUE", "position": pos})
                self._log(f"[COORD] QUEUE {client_id} at pos {pos}")

    def release_cs(self, client_id):
        with self.lock:
            if self.in_cs == client_id:
                self._log(f"[COORD] RELEASE <- {client_id}")
                self.in_cs = None
                self.in_cs_since = 0.0
                self._grant_next_locked()

    def on_disconnect(self, client_id):
        with self.lock:
            removed = False
            try:
                self.queue.remove(client_id)
                removed = True
            except:
                pass

            if self.in_cs == client_id:
                self._log(f"[COORD] {client_id} disconnected while in CS -> revoke.")
                self.in_cs = None
                self.in_cs_since = 0.0
                self._grant_next_locked()

            elif removed:
                self._log(f"[COORD] {client_id} removed from queue.")

    def _grant_next_locked(self):
        if self.queue:
            next_id = self.queue.popleft()
            self.in_cs = next_id
            self.in_cs_since = time.time()
            self._send_grant(next_id)
