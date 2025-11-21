#server TCP + whitelist IP
# server_main.py
import socket, threading, json, argparse, sys, time
from coordinator import Coordinator
from protocol import send_json

# ============================
# 1) SỐ DƯ CLIENT & TỔNG TIỀN ATM
# ============================
balances = {
    "A000": 5000000,
    "A001": 5000000,
    "A002": 3000000,
    "A003": 10000000,
    "A004": 7000000
}
default_balance = 5000000

# ⭐ Tổng số tiền trong ATM
atm_total = 20000000   # 20 triệu


def handle_client(sock, addr, coordinator, allowed_ips, clients, clients_lock, id_by_sock, print_lock):
    global atm_total
    ip, port = addr
    with print_lock:
        print(f"[NET] New connection from {ip}:{port}")
        sys.stdout.flush()

    if allowed_ips and ip not in allowed_ips:
        send_json(sock, {"type": "DENY", "reason": "not_whitelisted"})
        sock.close()
        return

    client_id = None
    buffer = ""

    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            buffer += data.decode("utf-8", errors="ignore")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                mtype = msg.get("type")

                # ============================
                # REGISTER
                # ============================
                if mtype == "REGISTER":
                    candidate = msg.get("client_id") or f"client_{ip}_{port}"

                    with clients_lock:
                        if candidate in clients and clients[candidate] is not sock:
                            candidate = f"{candidate}_{int(time.time())}"
                        client_id = candidate
                        clients[client_id] = sock
                        id_by_sock[sock] = client_id

                    # Nếu chưa có số dư thì tạo mới
                    if client_id not in balances:
                        balances[client_id] = default_balance

                    send_json(sock, {
                        "type": "REGISTERED",
                        "client_id": client_id,
                        "balance": balances.get(client_id, 0),
                        "atm_balance": atm_total
                    })

                # ============================
                # REQUEST
                # ============================
                elif mtype == "REQUEST" and client_id:
                    coordinator.request_cs(client_id)

                # ============================
                # RELEASE
                # ============================
                elif mtype == "RELEASE" and client_id:
                    coordinator.release_cs(client_id)

                # ============================
                # WITHDRAW
                # ============================
                elif mtype == "WITHDRAW" and client_id:

                    amount = int(msg.get("amount", 0))
                    old_balance = balances.get(client_id, default_balance)

                    # ⭐ check tiền tài khoản
                    if amount <= 0:
                        send_json(sock, {"type": "ATM_ERROR", "msg": "Invalid amount"})
                        continue

                    if amount > old_balance:
                        send_json(sock, {"type": "ATM_ERROR", "msg": "Insufficient funds"})
                        continue

                    # ⭐ check ATM còn đủ tiền không

                    if amount > atm_total:
                        send_json(sock, {
                            "type": "ATM_ERROR",
                            "msg": "ATM is out of cash!"
                        })
                        continue

                    # ⭐ Trừ tiền
                    new_balance = old_balance - amount
                    balances[client_id] = new_balance

                    atm_total -= amount   # ⭐ trừ tiền ATM

                    # ⭐ gửi thông tin mới
                    send_json(sock, {
                        "type": "ATM_OK",
                        "new_balance": new_balance,
                        "atm_balance": atm_total
                    })

    except Exception:
        pass

    finally:
        # cleanup
        if client_id:
            coordinator.on_disconnect(client_id)

        with clients_lock:
            try:
                id_by_sock.pop(sock, None)
                if client_id in clients and clients[client_id] is sock:
                    clients.pop(client_id, None)
            except:
                pass

        try:
            sock.close()
        except:
            pass


def main():
    parser = argparse.ArgumentParser(description="Centralized Mutual Exclusion Server (Coordinator)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--allow", action="append", default=[])
    parser.add_argument("--lease", type=int, default=None)
    args = parser.parse_args()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((args.host, args.port))
    srv.listen(16)

    print_lock = threading.Lock()
    clients_lock = threading.Lock()
    clients = {}
    id_by_sock = {}

    coord = Coordinator(
        clients,
        balances,
        lambda: atm_total,
        print_lock=print_lock,
        lease_secs=args.lease
    )

    print(f"[BOOT] Server running on {args.host}:{args.port}")

    while True:
        sock, addr = srv.accept()
        t = threading.Thread(target=handle_client,
                             args=(sock, addr, coord, set(args.allow), clients, clients_lock, id_by_sock, print_lock),
                             daemon=True)
        t.start()


if __name__ == "__main__":
    main()
