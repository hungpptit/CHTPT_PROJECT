# 🏧 ATM Mutual Exclusion System (Python + Socket)

Hệ thống mô phỏng ATM sử dụng Centralized Coordinator để đảm bảo Mutual Exclusion, xử lý rút tiền, đồng bộ số dư và hỗ trợ kết nối từ xa qua **ngrok TCP**.

---

## 📋 Mục Lục
- [Tổng Quan](#tổng-quan)
- [Yêu Cầu Hệ-Thống](#yêu-cầu-hệ-thống)
- [Clone-Dự-Án](#clone-dự-án)
- [Tạo-Môi-Trường-Virtualenv](#tạo-môi-trường-virtualenv)
- [Cài-Đặt-Dependencies](#cài-đặt-dependencies)
- [Chạy-Server](#chạy-server)
- [Expose-Server-bằng-ngrok-TCP](#expose-server-bằng-ngrok-tcp)
- [Chạy-Client-Python](#chạy-client-python)
- [Chạy-Client-EXE](#chạy-client-exe)
- [Build-File-EXE](#build-file-exe)
- [Cấu-Trúc-Dự-Án](#cấu-trúc-dự-án)
- [requirements.txt](#requirementstxt)

---

## 🎯 Tổng Quan
Dự án gồm hai thành phần:

1. **Server / Coordinator**
   - Điều phối REQUEST / RELEASE
   - Xử lý rút tiền (WITHDRAW)
   - Giữ hàng đợi FIFO đảm bảo Mutual Exclusion
   - Quản lý số dư tài khoản + số dư ATM

2. **Client ATM GUI**
   - Giao diện Tkinter mô phỏng máy ATM
   - Popup nhập số tiền (tự format 3,000,000)
   - Hỗ trợ chạy dạng Python hoặc dạng file `.exe`

---

## 🖥 Yêu Cầu Hệ Thống
- Python 3.10+
- pip
- Ngrok 

---

## 📦 Clone Dự Án

```
git clone https://github.com/hungpptit/CHTPT_PROJECT.git
cd CHTPT_PROJECT
```

---

## 🧩 Tạo Môi Trường Virtualenv

```
python -m venv .venv
```

Kích hoạt (Windows):

```
.\.venv\Scripts\activate
```

---

## ⚙ Cài Đặt Dependencies

```
pip install -r requirements.txt
```

---

## 🚀 Chạy Server (Local LAN hoặc chạy với Ngrok)

Chạy mặc định:

```
python server_main.py
```

Chạy với tuỳ chọn:

```
python server_main.py --host 0.0.0.0 --port 5000
```

Whitelisting IP (tuỳ chọn):

```
python server_main.py --host 0.0.0.0 --port 5000 --allow 127.0.0.1
```

---

## 🌐 Expose Server bằng ngrok TCP

### 1. Login và thêm token

```
ngrok config add-authtoken <YOUR_TOKEN>
```

### 2. Mở tunnel TCP cho server (port 5000)

```
ngrok tcp 5000
```

Bạn sẽ nhận được địa chỉ dạng:

```
tcp://0.tcp.ap.ngrok.io:18825
```

### 3. Điền host + port này vào Client GUI:

```
Host: 0.tcp.ap.ngrok.io
Port: 18825
```

---

## 💻 Chạy Client Python

Kích hoạt venv nếu có:

```
.\.venv\Scripts\activate
```

Chạy:

```
python client_gui.py
```

---

## 🟦 Chạy Client EXE (không cần Python)

Chạy trực tiếp:

```
dist/ATM_Client.exe
```

Không cần cài bất kỳ thư viện nào.

---

## 🏗 Build File EXE

```
pyinstaller --noconsole --onefile --name ATM_Client client_gui.py
```

Kết quả:

```
dist/ATM_Client.exe
build/
ATM_Client.spec
```

---

## 📁 Cấu Trúc Dự Án

```
CHTPT_PROJECT/
│  server_main.py
│  client_gui.py
│  client_net.py
│  coordinator.py
│  protocol.py
│  README.md
│  requirements.txt
│
├─dist/
│   └── ATM_Client.exe
├─build/
└─.venv/
```

---

## 📦 requirements.txt

```
pyinstaller
```

---

README này bao gồm:
- Clone dự án
- Tạo venv
- Cài đặt trong venv
- Chạy server
- Chạy server qua ngrok
- Chạy client Python
- Chạy client exe
- Build lại exe
- Cấu trúc thư mục chuẩn

