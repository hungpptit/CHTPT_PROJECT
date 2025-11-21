# app desktop Tkinter - ATM Edition (FULL)
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import queue, time
from client_net import ClientNetwork


class ClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ATM Mutual Exclusion Client")
        self.geometry("720x550")
        self.configure(bg="#f4f7fb")

        # Style đẹp
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Arial", 10), padding=6)
        style.configure("TLabel", background="#f4f7fb", font=("Arial", 10))
        style.configure("TLabelframe", background="#f4f7fb", font=("Arial", 11, "bold"))
        style.configure("TLabelframe.Label", font=("Arial", 11, "bold"))

        self.net = None
        self.inbox = queue.Queue()

        self.state = tk.StringVar(value="DISCONNECTED")
        self.client_id = tk.StringVar(value=f"A00{int(time.time())%10}")
        self.server_host = tk.StringVar(value="0.tcp.ap.ngrok.io")
        self.server_port = tk.IntVar(value=18825)

        # ⭐ số dư của client
        self.current_balance = tk.StringVar(value="N/A")

        # ⭐ số dư tổng ATM
        self.atm_total_balance = tk.StringVar(value="N/A")

        self._build_ui()

        self.atm_window = None
        self.atm_result_var = None

        self.after(60, self._process_inbox)

    # ===============================
    # UI SETUP
    # ===============================
    def _build_ui(self):
        # ---- CONNECT FORM ----
        frm_conn = ttk.LabelFrame(self, text="Kết nối Server")
        frm_conn.pack(fill="x", padx=10, pady=8)

        ttk.Label(frm_conn, text="Server:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(frm_conn, textvariable=self.server_host, width=22).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frm_conn, text="Port:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ttk.Entry(frm_conn, textvariable=self.server_port, width=8).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frm_conn, text="Client ID:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        ttk.Entry(frm_conn, textvariable=self.client_id, width=12).grid(row=0, column=5, padx=5, pady=5)

        self.btn_connect = ttk.Button(frm_conn, text="Connect", command=self.on_connect)
        self.btn_connect.grid(row=0, column=6, padx=8)

        self.btn_disconnect = ttk.Button(frm_conn, text="Disconnect",
                                         command=self.on_disconnect, state="disabled")
        self.btn_disconnect.grid(row=0, column=7, padx=8)

        # ---- STATUS ----
        frm_ctrl = ttk.LabelFrame(self, text="Trạng thái & Điều khiển")
        frm_ctrl.pack(fill="x", padx=10, pady=8)

        ttk.Label(frm_ctrl, text="Trạng thái:").grid(row=0, column=0, padx=6, pady=5)
        ttk.Label(frm_ctrl, textvariable=self.state,
                  foreground="#0078D4", font=("Arial", 11, "bold")).grid(row=0, column=1, padx=6, pady=5)

        ttk.Label(frm_ctrl, text="Số dư tài khoản:").grid(row=1, column=0, padx=6, pady=5)
        ttk.Label(frm_ctrl, textvariable=self.current_balance,
                  font=("Arial", 11, "bold"), foreground="#2d6a4f").grid(row=1, column=1, padx=6, pady=5)

        ttk.Label(frm_ctrl, text="Tiền còn lại trong ATM:").grid(row=2, column=0, padx=6, pady=5)
        ttk.Label(frm_ctrl, textvariable=self.atm_total_balance,
                  font=("Arial", 11, "bold"), foreground="#8a5ef8").grid(row=2, column=1, padx=6, pady=5)

        self.btn_request = ttk.Button(frm_ctrl, text="💸 Withdraw (REQUEST)",
                                      command=self.on_request, state="disabled")
        self.btn_request.grid(row=0, column=2, padx=10)

        self.btn_release = ttk.Button(frm_ctrl, text="✔ Release",
                                      command=self.on_release, state="disabled")
        self.btn_release.grid(row=0, column=3, padx=10)

        # ---- LOG ----
        frm_log = ttk.LabelFrame(self, text="Logs")
        frm_log.pack(fill="both", expand=True, padx=10, pady=8)

        self.txt = ScrolledText(frm_log, height=15, font=("Consolas", 10))
        self.txt.pack(fill="both", expand=True)

    def log(self, s):
        self.txt.insert("end", s + "\n")
        self.txt.see("end")

    # ===============================
    # CONNECT / DISCONNECT
    # ===============================
    def on_connect(self):
        if self.net:
            return
        host = self.server_host.get().strip()
        port = int(self.server_port.get())
        cid = self.client_id.get().strip()

        self.net = ClientNetwork(host, port, cid, self.inbox, self._on_net_disconnected)
        self.net.start()

        self.state.set("CONNECTING")
        self.btn_connect.config(state="disabled")
        self.btn_disconnect.config(state="normal")
        self.log(f"[UI] Connecting to {host}:{port} as {cid}...")

    def on_disconnect(self):
        if self.net:
            self.net.stop()
        self._on_net_disconnected()

    def _on_net_disconnected(self):
        self.state.set("DISCONNECTED")
        self.btn_connect.config(state="normal")
        self.btn_disconnect.config(state="disabled")
        self.btn_request.config(state="disabled")
        self.btn_release.config(state="disabled")
        self.current_balance.set("N/A")
        self.atm_total_balance.set("N/A")
        self.net = None
        self.log("[NET] Disconnected.")

    # ===============================
    # MUTEX ACTIONS
    # ===============================
    def on_request(self):
        if self.net:
            self.net.request_cs()
            self.state.set("WAITING")
            self.btn_request.config(state="disabled")
            self.log("[APP] REQUEST sent.")

    def on_release(self):
        if self.net:
            self.net.release_cs()
        self.state.set("IDLE")
        self.btn_request.config(state="normal")
        self.btn_release.config(state="disabled")
        self.log("[APP] RELEASE sent.")

        if self.atm_window:
            self.atm_window.destroy()
            self.atm_window = None

    # ===============================
    # POPUP ATM WINDOW (ĐẸP)
    # ===============================
    def open_atm_popup(self, balance, atm_balance):
        win = tk.Toplevel(self)
        win.title("💳 ATM Withdrawal")
        win.geometry("360x330")
        win.resizable(False, False)

        # Màu nền hiện đại
        win.configure(bg="#eef4fb")

        # ===== Title =====
        title = tk.Label(
            win,
            text=f"Số dư tài khoản: {balance:,} đ",
            font=("Segoe UI", 14, "bold"),
            bg="#eef4fb",
            fg="#0b4da2"
        )
        title.pack(pady=(20, 5))

        atm_label = tk.Label(
            win,
            text=f"Tiền còn trong ATM: {atm_balance:,} đ",
            font=("Segoe UI", 12),
            bg="#eef4fb",
            fg="#7d4cd1"
        )
        atm_label.pack(pady=(0, 20))

        # ===== Input Label =====
        tk.Label(
            win,
            text="Nhập số tiền muốn rút:",
            font=("Segoe UI", 11),
            bg="#eef4fb"
        ).pack()

        # ===== Entry format tiền =====
        amount_var = tk.StringVar()

        entry = ttk.Entry(win, textvariable=amount_var, width=18, font=("Segoe UI", 11))
        entry.pack(pady=8)

        # Format tự động: "3000000" → "3,000,000"
        def format_amount(*args):
            txt = amount_var.get().replace(",", "")
            if txt.isdigit():
                amount_var.set(f"{int(txt):,}")

        amount_var.trace_add("write", format_amount)

        # ===== Result Label =====
        self.atm_result_var = tk.StringVar()
        result_label = tk.Label(
            win,
            textvariable=self.atm_result_var,
            font=("Segoe UI", 11),
            bg="#eef4fb",
            fg="#0078d7"
        )
        result_label.pack(pady=10)

        # ===== Button =====
        def do_withdraw():
            raw = amount_var.get().replace(",", "")
            if not raw.isdigit():
                self.atm_result_var.set("❌ Vui lòng nhập số hợp lệ.")
                return

            amount = int(raw)
            self.net.withdraw(amount)
            self.atm_result_var.set("⏳ Đang xử lý...")

        modern_btn = tk.Button(
            win,
            text="💰 Rút tiền",
            command=do_withdraw,
            bg="#0b63c9",
            fg="white",
            activebackground="#094a96",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=10, pady=6
        )
        modern_btn.pack(pady=12)

        # Lưu window để auto close khi Release
        self.atm_window = win

    # ===============================
    # PROCESS SERVER MESSAGES
    # ===============================
    def _process_inbox(self):
        try:
            while True:
                msg = self.inbox.get_nowait()
                t = msg.get("type")

                if t == "REGISTERED":
                    self.state.set("IDLE")

                    # ⭐ lấy số dư tài khoản
                    bal = int(msg.get("balance", 0))
                    atm_bal = int(msg.get("atm_balance", 0))

                    # ⭐ cập nhật GUI
                    self.current_balance.set(f"{bal:,} đ")
                    self.atm_total_balance.set(f"{atm_bal:,} đ")

                    self.btn_request.config(state="normal")
                    self.log(f"[NET] Registered as {msg.get('client_id')} | balance={bal:,} | atm={atm_bal:,}")

                elif t == "GRANT":
                    bal = int(msg.get("balance", 0))
                    atm_bal = int(msg.get("atm_balance", 0))

                    # cập nhật GUI chính
                    self.current_balance.set(f"{bal:,} đ")
                    self.atm_total_balance.set(f"{atm_bal:,} đ")

                    self.state.set("IN_CS")
                    self.btn_release.config(state="normal")
                    self.log(f"[COORD] GRANT received.")

                    self.open_atm_popup(bal, atm_bal)

                elif t == "QUEUE":
                    self.log(f"[COORD] Waiting. Queue position: {msg.get('position')}")

                elif t == "ATM_OK":
                    new_bal = int(msg.get("new_balance"))
                    atm_bal = int(msg.get("atm_balance"))

                    self.current_balance.set(f"{new_bal:,} đ")
                    self.atm_total_balance.set(f"{atm_bal:,} đ")

                    if self.atm_result_var:
                        self.atm_result_var.set(
                            f"✔ Thành công! Số dư mới: {new_bal:,} đ")

                    self.log(f"[ATM] Withdraw OK.")

                    self.after(1200, self.on_release)

                elif t == "ATM_ERROR":
                    if self.atm_result_var:
                        self.atm_result_var.set("❌ " + msg.get("msg"))
                    self.log(f"[ATM] Error: {msg.get('msg')}")

                else:
                    self.log(f"[NET] {msg}")

        except queue.Empty:
            pass

        self.after(60, self._process_inbox)


if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()
