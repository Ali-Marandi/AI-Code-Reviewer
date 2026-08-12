# مستند جامع تخصصی: قفل سخت‌افزاری، امضای دیجیتال و به‌روزرسانی خودکار دسکتاپ

این سند سه بخش حیاتی از توسعه حرفه‌ای و تجاری نرم‌افزار دسکتاپ **AI-Code-Reviewer Enterprise** را پوشش می‌دهد:
1. **قفل سخت‌افزاری و لایسنس مبتنی بر گره (Node-Locked Licensing)**
2. **پایپ‌لاین کامل CI/CD برای امضای دیجیتال (Code Signing) و ساخت MSI**
3. **سیستم به‌روزرسانی خودکار درون‌برنامه‌ای (In-App Auto-Update)**

---

## ۱. قفل سخت‌افزاری و لایسنس مبتنی بر گره (Node-Locked Licensing)

برای جلوگیری از اشتراک‌گذاری غیرمجاز لایسنس بین چندین سیستم، نسخه اینترپرایز از مدل **Node-Locked** استفاده می‌کند. در این روش، کلید لایسنس به سخت‌افزار مشخصی از دستگاه کاربر گره می‌خورد.

### الف. استخراج اثر انگشت سخت‌افزاری در کلاینت (Python):
نرم‌افزار دسکتاپ پارامترهای پایداری مثل شماره سریال مادربرد، پردازنده و آدرس مک را ترکیب و هش می‌کند:
```python
import platform
import subprocess
import hashlib

def get_node_fingerprint() -> str:
    try:
        # در ویندوز دریافت سریال مادربرد از طریق WMI
        cmd = "wmic baseboard get serialnumber"
        serial = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
    except Exception:
        serial = platform.node()
    
    raw_id = f"{platform.processor()}-{serial}-{platform.machine()}"
    return hashlib.sha256(raw_id.encode('utf-8')).hexdigest()
```

### ب. بررسی و اعتبارسنجی در لایسنس سرور (FastAPI):
سرور بررسی می‌کند که آیا این دستگاه مجاز به استفاده از کلید لایسنس است یا خیر:
```python
@app.post("/api/v1/license/validate-node")
def validate_node(license_key: str, fingerprint: str, db: Session = Depends(get_db)):
    license_rec = db.query(LicenseModel).filter_by(key=license_key, active=True).first()
    if not license_rec:
        raise HTTPException(status_code=403, detail="Invalid license key.")
    
    # بررسی لیست دستگاه‌های ثبت‌شده برای این لایسنس
    device = db.query(DeviceModel).filter_by(license_key=license_key, fingerprint=fingerprint).first()
    if not device:
        active_count = db.query(DeviceModel).filter_by(license_key=license_key).count()
        if active_count >= license_rec.max_seats:
            raise HTTPException(status_code=400, detail="Node limit reached for this license.")
        
        # ثبت دستگاه جدید
        new_device = DeviceModel(license_key=license_key, fingerprint=fingerprint)
        db.add(new_device)
        db.commit()
    
    return {"status": "authorized", "organization": license_rec.org_name}
```

---

## ۲. پایپ‌لاین کامل CI/CD برای امضای دیجیتال (Code Signing) و ساخت MSI

برای جلوگیری از اخطارهای امنیتی ویندوز (Windows Defender SmartScreen)، فایل‌های خروجی باید با گواهی معتبر دیجیتال امضا شوند.

### اسکریپت کامل `.github/workflows/build.yml`:
```yaml
name: Build, Sign and Release MSI

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build-and-sign:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install Dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build Standalone EXE
      run: |
        pyinstaller --onefile --windowed --name AI-Code-Reviewer app.py
    - name: Import Code Signing Certificate
      run: |
        # وارد کردن گواهی دیجیتال (PFX) از GitHub Secrets
        $certBytes = [System.Convert]::FromBase64String("${{ secrets.CERTIFICATE_BASE64 }}")
        [System.IO.File]::WriteAllBytes("cert.pfx", $certBytes)
        certutil -p "${{ secrets.CERTIFICATE_PASSWORD }}" -importcert cert.pfx
      shell: pwsh
    - name: Sign Executable (Code Signing)
      run: |
        # امضای دیجیتال فایل EXE با ابزار Signtool
        signtool sign /f cert.pfx /p "${{ secrets.CERTIFICATE_PASSWORD }}" /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 dist/AI-Code-Reviewer.exe
      shell: pwsh
    - name: Build MSI Installer
      run: |
        dotnet tool install --global WiX.Toolset
        # دستورات ساخت MSI با WiX
      shell: pwsh
    - name: Sign MSI Installer
      run: |
        signtool sign /f cert.pfx /p "${{ secrets.CERTIFICATE_PASSWORD }}" /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 dist/AI-Code-Reviewer-Enterprise.msi
      shell: pwsh
    - name: Publish to GitHub Releases
      uses: softprops/action-gh-release@v2
      with:
        files: dist/AI-Code-Reviewer-Enterprise.msi
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## ۳. سیستم به‌روزرسانی خودکار درون‌برنامه‌ای (In-App Auto-Update)

برای اینکه کاربران نسخه جدید را بدون نیاز به دانلود دستی دریافت کنند، اپلیکیشن دسکتاپ در زمان راه‌اندازی، نسخه خود را با فایل `latest.json` روی سرور مقایسه می‌کند.

### پیاده‌سازی چک کردن به‌روزرسانی در کلاینت (Python / PySide6):
```python
import requests
from PySide6.QtWidgets import QMessageBox
import webbrowser

CURRENT_VERSION = "1.0.2"
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/Ali-Marandi/AI-Code-Reviewer/main/latest.json"

def check_for_updates(parent_widget=None):
    try:
        response = requests.get(UPDATE_CHECK_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("version")
            download_url = data.get("download_url")
            
            if latest_version and latest_version != CURRENT_VERSION:
                reply = QMessageBox.question(
                    parent_widget,
                    "Update Available",
                    f"A new version ({latest_version}) of AI-Code-Reviewer is available!\nWould you like to download it now?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    webbrowser.open(download_url)
    except Exception as e:
        print(f"Update check failed: {str(e)}")
```
این تابع را می‌توان هنگام اجرای اولیه برنامه (`MainWindow.__init__`) فراخوانی کرد تا کاربر همیشه از انتشار نسخه‌های جدید مطلع شود.
