# راهنمای جامع بهینه‌سازی نهایی: بسته‌بندی MSI، داشبورد ابری و طراحی تم مدرن دسکتاپ

این سند سه بخش پایانی و تخصصی توسعه‌ی نسخه اینترپرایز را بررسی می‌کند:
1. **بهینه‌سازی پایپ‌لاین CI/CD برای ساخت Windows Installer (MSI)**
2. **معماری داشبورد مانیتورینگ تله‌متری و مدیریت لایسنس‌های سازمانی**
3. **طراحی و پیاده‌سازی پوسته (Theme) مدرن و حرفه‌ای با PySide6**

---

## ۱. بهینه‌سازی پایپ‌لاین CI/CD برای ساخت Windows Installer (MSI)

برای توزیع نرم‌افزار در سازمان‌ها، فایل‌های اجرایی ساده (`.exe`) کافی نیستند و نیاز به بسته‌های نصب استاندارد ویندوز (`.msi`) مجهز به قابلیت نصب صامت (Silent Install) و میانبرهای سیستم است. ابزار **WiX Toolset** یا **pynsist** گزینه‌های عالی هستند.

### نمونه به‌روزرسانی `.github/workflows/build.yml` برای ساخت MSI:
```yaml
name: Build Windows MSI Installer

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build-msi:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install dependencies & PyInstaller
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build Standalone EXE
      run: |
        pyinstaller --onedir --windowed --name AI-Code-Reviewer app.py
    - name: Install WiX Toolset & Build MSI
      run: |
        dotnet tool install --global WiX.Toolset
        # دستورات بسته‌بندی خروجی PyInstaller به فرمت MSI با WiX
      shell: pwsh
    - name: Release MSI Asset
      uses: softprops/action-gh-release@v2
      with:
        files: dist/AI-Code-Reviewer-Enterprise.msi
        overwrite_files: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## ۲. معماری داشبورد مانیتورینگ تله‌متری و مدیریت لایسنس‌های سازمانی

برای مدیران فناوری سازمان (CTO / IT Admins)، داشتن یک پنل متمرکز برای کنترل لایسنس‌ها و بررسی سلامت نرم‌افزارهای دسکتاپ نصب‌شده ضروری است.

### الف. ساختار پایگاه داده مدیریت لایسنس (SQL Schema):
```sql
CREATE TABLE licenses (
    license_key VARCHAR(64) PRIMARY KEY,
    organization_name VARCHAR(128) NOT NULL,
    max_seats INT NOT NULL,
    active_seats INT DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE
);

CREATE TABLE device_activations (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(64) REFERENCES licenses(license_key),
    hardware_fingerprint VARCHAR(128) NOT NULL,
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### ب. اندپوینت اعتبارسنجی لایسنس در بک‌اند سازمانی (FastAPI):
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class LicenseRequest(BaseModel):
    license_key: str
    hardware_fingerprint: str

@app.post("/api/v1/license/verify")
def verify_license(req: LicenseRequest):
    # بررسی صحت کلید و وضعیت سخت‌افزار در دیتابیس
    return {"status": "valid", "tier": "enterprise", "expires": "2027-12-31"}
```

---

## ۳. پیاده‌سازی پوسته (Theme) مدرن و حرفه‌ای در PySide6

برای رقابت با نرم‌افزارهای مدرن بازار، رابط کاربری با پالت رنگی الهام‌گرفته از **Fluent Design** و **VS Code Dark+** استایل‌دهی می‌شود.

### استایل‌سیت پیشرفته (`ui/theme.py`):
```python
MODERN_DARK_STYLESHEET = """
QMainWindow {
    background-color: #18181b;
}
QWidget {
    background-color: #18181b;
    color: #f4f4f5;
    font-family: 'Segoe UI', -apple-system, sans-serif;
    font-size: 13px;
}
QFrame#Sidebar {
    background-color: #202024;
    border-right: 1px solid #27272a;
}
QPushButton {
    background-color: #27272a;
    border: 1px solid #3f3f46;
    color: #fafafa;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #3f3f46;
    border-color: #52525b;
}
QPushButton#PrimaryButton {
    background-color: #007acc;
    border: none;
    color: white;
}
QPushButton#PrimaryButton:hover {
    background-color: #0098ff;
}
QTableWidget {
    background-color: #202024;
    border: 1px solid #27272a;
    gridline-color: #27272a;
    border-radius: 6px;
}
QHeaderView::section {
    background-color: #27272a;
    color: #a1a1aa;
    padding: 8px;
    border: none;
    font-weight: bold;
}
QLineEdit {
    background-color: #27272a;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 8px;
    color: white;
}
QLineEdit:focus {
    border-color: #007acc;
}
"""
```

این استایل به راحتی در فایل `ui/main_window.py` اعمال می‌شود تا ظاهر نرم‌افزار کاملاً حرفه‌ای و مطابق با استانداردهای جهانی تجاری به نظر برسد.
