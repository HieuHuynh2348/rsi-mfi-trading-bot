# 🔧 FIX: Binance API Restricted Location Error

## ❌ Vấn đề:

```
ERROR: Service unavailable from a restricted location according to 
'b. Eligibility' in https://www.binance.com/en/terms
```

**Nguyên nhân:**
- Vercel servers ở US/Europe
- Binance CHẶN một số khu vực
- API call từ Vercel → BỊ REJECT! 🚫

---

## ✅ GIẢI PHÁP 1: Chạy Bot LOCAL (RECOMMENDED)

### Bước 1: Chạy bot trên máy tính
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Chạy bot
python main.py
```

**Kết quả:**
- ✅ Chạy từ IP Việt Nam → Binance cho phép
- ✅ Scan liên tục mỗi 5 phút tự động
- ✅ Gửi Telegram khi có tín hiệu
- ✅ KHÔNG CẦN Vercel, KHÔNG CẦN Cron-Job.org

### Bước 2: Giữ máy bật 24/7
- Để máy tính chạy liên tục
- Hoặc chạy khi cần trading
- Bot tự động scan theo SCAN_INTERVAL (5 phút)

---

## ✅ GIẢI PHÁP 2: Windows Task Scheduler

Nếu không muốn giữ terminal mở:

### Tạo file run_bot.bat:
```batch
@echo off
cd /d "H:\BOT UPGRADE"
call .venv\Scripts\activate.bat
python main.py
pause
```

### Setup Task Scheduler:
1. Mở Task Scheduler
2. Create Task:
   - Name: "RSI MFI Trading Bot"
   - Trigger: At startup
   - Action: Run `H:\BOT UPGRADE\run_bot.bat`
3. Bot tự chạy mỗi khi khởi động Windows

---

## ✅ GIẢI PHÁP 3: Deploy lên VPS ở Việt Nam/Singapore

### VPS Options:
1. **Vultr Singapore** ($5/tháng)
   - IP Singapore → Binance cho phép
   - Setup: Ubuntu + Python + Cron

2. **DigitalOcean Singapore** ($6/tháng)
   - Same as above

3. **AWS EC2 ap-southeast-1** (Singapore)
   - Free tier 12 tháng
   - Sau đó $3-5/tháng

### Setup trên VPS:
```bash
# 1. Clone code
git clone <your-repo>
cd trading-bot

# 2. Install Python + dependencies
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt

# 3. Setup .env file
nano .env
# Paste API keys

# 4. Setup cron
crontab -e
# Add:
*/5 * * * * cd /path/to/bot && python3 main.py

# 5. Test
python3 main.py
```

---

## ✅ GIẢI PHÁP 4: Binance US API (nếu ở US)

Nếu muốn dùng Vercel:
```python
# binance_client.py
from binance.client import Client

# Thay vì:
client = Client(api_key, api_secret)

# Dùng:
client = Client(
    api_key, 
    api_secret,
    tld='us'  # Binance US
)
```

**Nhược điểm:**
- Chỉ hoạt động nếu có tài khoản Binance US
- Ít coins hơn Binance Global

---

## ✅ GIẢI PHÁP 5: Proxy/VPN trên Vercel (Phức tạp)

**KHÔNG KHUYẾN NGHỊ** vì:
- Vi phạm Terms of Service của Binance
- Phức tạp, không ổn định
- Risk bị ban account

---

## 🎯 SO SÁNH GIẢI PHÁP:

| Giải pháp | Chi phí | Độ khó | Ổn định | Khuyến nghị |
|-----------|---------|--------|---------|-------------|
| **Local (main.py)** | FREE | ⭐ Dễ | ⭐⭐⭐ | ✅ **BEST** |
| **Task Scheduler** | FREE | ⭐⭐ TB | ⭐⭐⭐ | ✅ Good |
| **VPS Singapore** | $5/tháng | ⭐⭐⭐ Khó | ⭐⭐⭐⭐ | ✅ Pro |
| **Binance US** | FREE | ⭐⭐ TB | ⭐⭐ | ⚠️ Limited |
| **Proxy** | Varies | ⭐⭐⭐⭐ | ⭐ | ❌ Risky |

---

## 🚀 KHUYẾN NGHỊ NGAY:

### Chạy bot local NGAY:

```powershell
# 1. Vào thư mục bot
cd "H:\BOT UPGRADE"

# 2. Activate environment
.\.venv\Scripts\Activate.ps1

# 3. Chạy bot
python main.py
```

**Màn hình sẽ hiển thị:**
```
🤖 Trading Bot Started!
⏰ Scan interval: 300 seconds (5 minutes)
📊 Scanning 348 symbols on Binance...

[12:00:00] 🔍 Scanning market...
[12:00:05] ✅ Found 15 signals
[12:00:06] 📱 Sent to Telegram

[12:05:00] 🔍 Scanning market...
...
```

**Bot sẽ:**
- ✅ Scan mỗi 5 phút tự động
- ✅ Gửi Telegram khi có tín hiệu
- ✅ Chạy mãi cho đến khi bạn tắt (Ctrl+C)

---

## 📝 Tạo Service Windows (Advanced):

Nếu muốn chạy như Windows Service:

### File: install_service.py
```python
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path

class TradingBotService(win32serviceutil.ServiceFramework):
    _svc_name_ = "RSIMFITradingBot"
    _svc_display_name_ = "RSI+MFI Trading Bot"
    _svc_description_ = "Automated trading bot for Binance"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def main(self):
        # Import và chạy bot
        os.chdir(Path(__file__).parent)
        from main import TradingBot
        bot = TradingBot()
        bot.run()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TradingBotService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(TradingBotService)
```

**Install:**
```powershell
pip install pywin32
python install_service.py install
python install_service.py start
```

---

## ⚠️ Về Vercel:

**Vercel KHÔNG DÙNG ĐƯỢC cho bot này vì:**
1. ❌ Binance chặn US/EU IPs
2. ❌ Function timeout 10s (quá ngắn)
3. ❌ Không có cron (FREE plan)

**→ Vercel chỉ phù hợp cho:**
- Web apps
- API không giới hạn địa lý
- Serverless functions nhẹ

---

## 📞 Support:

Nếu gặp lỗi khi chạy local:
```powershell
# Check Python
python --version

# Check dependencies
pip list

# Reinstall nếu cần
pip install -r requirements.txt

# Test Binance connection
python -c "from binance_client import BinanceClient; c = BinanceClient(); print(c.get_all_symbols()[:5])"
```

---

## ✅ TÓM TẮT:

**Vấn đề:** Vercel IP bị Binance chặn

**Giải pháp tốt nhất:** 
```powershell
cd "H:\BOT UPGRADE"
.\.venv\Scripts\Activate.ps1
python main.py
```

**→ Giữ máy bật, bot chạy 24/7, GỬI TÍN HIỆU TỰ ĐỘNG!** 🚀

---

**Happy trading! 📊💰**
