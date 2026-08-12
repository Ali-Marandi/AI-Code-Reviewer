# راهنمای تخصصی و پیشرفته: تست محلی CI/CD، بک‌اِند لایسنس و استایل‌دهی سراسری PySide6

این مستند پاسخ‌های دقیق فنی به سه سوال پیشرفته شما درباره تست محلی اتوماسیون، پیاده‌سازی سرور لایسنس و شخصی‌سازی حرفه‌ای رابط کاربری دسکتاپ ارائه می‌دهد.

---

## ۱. نحوه بررسی و تست محلی GitHub Actions و ساخت MSI Installer

از آنجا که گیت‌هاب اکشنز روی سرورهای ابری اجرا می‌شود، برای تست محلی اسکریپت‌های ساخت (`build.yml`) بدون نیاز به ارسال کامیت‌های مکرر به گیت‌هاب، دو روش استاندارد وجود دارد:

### الف. ابزار `act` (اجرای محلی اکشن‌ها):
با نصب ابزار `act` (که از Docker برای شبیه‌سازی محیط GitHub Actions استفاده می‌کند)، می‌توانید پایپ‌لاین را روی سیستم خود اجرا کنید:
```bash
# نصب act در لینوکس/ویندوز
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# اجرای محلی کار (Job) مربوط به ساخت
act workflow_dispatch
```

### ب. تست محلی فرآیند PyInstaller و بسته‌بندی:
شما می‌توانید دستورات ساخت را مستقیماً در ترمینال ویندوز یا کانتینر خود تست کنید تا از صحت سوییچ‌ها اطمینان حاصل شود:
```bash
# نصب وابستگی‌ها
pip install -r requirements.txt pyinstaller

# ساخت فایل اجرایی تک‌پوشه
pyinstaller --onedir --windowed --name AI-Code-Reviewer app.py

# ساخت MSI با WiX Toolset (در محیط ویندوز)
dotnet tool install --global WiX.Toolset
heat dir dist/AI-Code-Reviewer -cg AppFiles -gg -sfrag -out fragment.wxs
candle product.wxs fragment.wxs
light product.wixobj -out AI-Code-Reviewer-Enterprise.msi
```

---

## ۲. جزئیات پیاده‌سازی سمت سرور (Backend) برای مدیریت لایسنس و اعتبارسنجی سخت‌افزاری

برای اینکه نرم‌افزار دسکتاپ بتواند لایسنس سازمان‌ها را اعتبارسنجی کند و از کپی غیرمجاز جلوگیری شود، بک‌اِند سرور (پیاده‌سازی‌شده با FastAPI و SQLAlchemy) به شکل زیر عمل می‌کند:

### الف. تولید اثر انگشت سخت‌افزاری (Hardware Fingerprint) در کلاینت (پایتون):
در نسخه دسکتاپ، قبل از ارسال درخواست به سرور، یک شناسه یکتا از مشخصات سخت‌افزاری سیستم استخراج می‌شود:
```python
import platform
import uuid
import hashlib

def get_hardware_fingerprint():
    # ترکیب نام سیستم، پردازنده و آدرس MAC مک‌ادرس شبکه
    system_info = f"{platform.node()}-{platform.processor()}-{uuid.getnode()}"
    return hashlib.sha256(system_info.encode('utf-8')).hexdigest()
```

### ب. بررسی و ثبت فعال‌سازی در سرور (FastAPI):
سرور بررسی می‌کند که آیا تعداد سیستم‌های فعال برای آن لایسنس از سقف مجاز (Max Seats) تجاوز نکرده باشد:
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

app = FastAPI()

class ActivationRequest(BaseModel):
    license_key: str
    hardware_fingerprint: str

@app.post("/api/v1/license/activate")
def activate_license(req: ActivationRequest, db: Session = Depends(get_db)):
    # ۱. بررسی وجود لایسنس و تاریخ انقضا
    license_record = db.query(LicenseModel).filter_by(license_key=req.license_key, is_revoked=False).first()
    if not license_record:
        raise HTTPException(status_code=404, detail="Invalid or revoked license key.")
    
    # ۲. بررسی اینکه آیا این دستگاه قبلاً ثبت شده است یا خیر
    existing_device = db.query(DeviceModel).filter_by(license_key=req.license_key, hardware_fingerprint=req.hardware_fingerprint).first()
    if existing_device:
        return {"status": "success", "message": "Device already activated."}
    
    # ۳. بررسی سقف تعداد کاربران مجاز (Seats)
    active_count = db.query(DeviceModel).filter_by(license_key=req.license_key).count()
    if active_count >= license_record.max_seats:
        raise HTTPException(status_code=400, detail="License seat limit reached.")
    
    # ۴. ثبت دستگاه جدید
    new_device = DeviceModel(license_key=req.license_key, hardware_fingerprint=req.hardware_fingerprint)
    db.add(new_device)
    db.commit()
    
    return {"status": "success", "message": "Activation successful."}
```

---

## ۳. نحوه اعمال سراسری و سفارشی‌سازی استایل‌شیت در PySide6

برای اینکه استایل مدرن تاریک (Modern Dark Theme) روی تمامی ویجت‌ها، دکمه‌ها، جدول‌ها و پنجره‌ها به صورت یکپارچه اعمال شود، باید استایل‌شیت را مستقیماً روی نمونه `QApplication` اعمال کنید (نه فقط `QMainWindow`):

### پیاده‌سازی در نقطه ورود برنامه (`app.py`):
```python
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.theme import MODERN_DARK_STYLESHEET

def run_gui(token):
    app = QApplication(sys.argv)
    
    # اعمال استایل‌شیت مدرن به صورت سراسری روی کل اپلیکیشن
    app.setStyleSheet(MODERN_DARK_STYLESHEET)
    
    github_client = GitHubClient(token)
    ai_engine = AIEngine()
    window = MainWindow(github_client, ai_engine)
    window.show()
    sys.exit(app.exec())
```

### سفارشی‌سازی پیشرفته اجزا (Widget Customization):
با استفاده از ویژگی `setObjectName` در پایتون، می‌توانید به ویجت‌های خاص استایل‌های اختصاصی بدهید:
```python
# مثال در main_window.py برای دکمه اصلی عملیات
btn_run_review = QPushButton("Run AI Enterprise Review")
btn_run_review.setObjectName("PrimaryButton") # اعمال استایل رنگ آبی متمایز از استایل‌شیت سراسری
```
این مکانیزم تضمین می‌کند که تمامی پنجره‌های پاپ‌آپ، جدول‌ها، فیلدهای متنی و دکمه‌ها دارای ظاهر یکپارچه، مدرن و حرفه‌ای باشند.
