# گزارش تکمیلی و راهنمای جامع AI-Code-Reviewer Enterprise

این مستند پاسخگوی درخواست‌های شما شامل بررسی فایل نقشه‌راه تجاری، وضعیت انتشار در گیت‌هاب و راهنمای سفارشی‌سازی اسکن امنیت پیشرفته (SAST) است.

---

## ۱. جزییات فایل نقشه‌راه تجاری (COMMERCIAL_ROADMAP.md)

نقشه‌راه تجاری این پروژه بر پایه استاندارد رقابت با نرم‌افزارهای پیشرو بازار (مانند SonarQube و GitHub Copilot Code Review) تدوین شده است و شامل سه محور اصلی زیر است:

- **موتور هوش مصنوعی پیشرفته (Advanced AI Engine):**
  - ارکستراسیون چندمدلی (Multi-Model Orchestration) برای جابجایی بین مدل‌های قدرتمند مانند GPT-4o و Claude 3.5 Sonnet.
  - ساخت گراف وابستگی‌های مخزن (Repository Context Graph) جهت درک تأثیر تغییرات یک فایل بر سایر بخش‌های پروژه.
  - موتور قوانین سفارشی سازمانی (Custom Enterprise Policies) برای اعمال خط‌مشی‌های امنیتی داخلی شرکت‌ها.

- **تجربه کاربری و رابط دسکتاپ اینترپرایز (Desktop UX):**
  - نمایش مقایسه‌ای تغییرات (Interactive Side-by-Side Diff Viewer).
  - اصلاح تک‌کلیکی (One-Click Quick Fix) و ثبت خودکار کامنت یا Commit در گیت‌هاب.
  - اجرای فرآیندهای سنگین در پس‌زمینه با استفاده از `QThread` جهت جلوگیری از فریز شدن برنامه.

- **امنیت، انطباق و گزارش‌دهی (Security & Compliance):**
  - اسکن پیشرفته نشت اطلاعات و کلیدهای مخفی (Secrets & PII Leakage Scanner).
  - تولید گزارش‌های مدیریتی (Executive PDF & JSON Reports) برای ارزیابی بدهی فنی (Technical Debt).
  - ذخیره‌سازی محلی امن با رمزنگاری پیشرفته (AES-256).

---

## ۲. وضعیت انتشار (Releases) و فایل‌های اجرایی در گیت‌هاب

وضعیت مخزن و انتشارات در گیت‌هاب (`Ali-Marandi/AI-Code-Reviewer`) به شرح زیر بررسی شد:
- **مخزن سورس‌کد:** تمامی فایل‌های سورس، شامل معماری ماژولار، کلاینت گیت‌هاب، موتور هوش مصنوعی و رابط کاربری PySide6 به‌روزرسانی و در شاخه `main` قرار گرفتند.
- **اتوماسیون ساخت (GitHub Actions):** فایل تنظیمات `.github/workflows/build.yml` برای کامپایل خودکار نرم‌افزار ویندوزی (`AI-Code-Reviewer-Enterprise.exe`) با استفاده از PyInstaller پیکربندی شد.
- **رفع خطای دسترسی انتشار:** دسترسی‌های نوشتاری (`permissions: contents: write`) به توکن اتوماسیون اضافه شد و تگ جدید `v1.0.2` جهت ساخت و انتشار نهایی در بخش **GitHub Releases** ارسال گردید.

---

## ۳. راهنمای سفارشی‌سازی اسکن امنیتی پیشرفته (SAST)

برای سفارشی‌سازی و توسعه قابلیت اسکن امنیتی پیشرفته (SAST) در این نرم‌افزار دسکتاپ، می‌توانید به دو روش اقدام کنید:

### الف. سفارشی‌سازی پرامپت سیستم و قوانین SAST در `core/ai_engine.py`
موتور هوش مصنوعی وظیفه تحلیل استاتیک و امنیتی کد را بر عهده دارد. شما می‌توانید با ویرایش متغیر `system_prompt` در کلاس `AIEngine`، قوانین امنیتی سخت‌گیرانه‌تری (مانند استانداردهای OWASP Top 10) اضافه کنید:

```python
system_prompt = (
    "You are an expert enterprise-grade code reviewer and senior SAST security auditor. "
    "Thoroughly analyze the code for OWASP Top 10 vulnerabilities (SQL Injection, XSS, CSRF, insecure deserialization, hardcoded secrets, etc.). "
    "Classify issues accurately into High, Medium, or Low severity, and provide secure remediation code in the suggestion field."
)
```

### ب. افزودن قوانین سفارشی محلی (Custom Regex / Pattern Matching)
برای ترکیب تحلیل ابزاری (Static Analysis) با هوش مصنوعی، می‌توانید پیش از ارسال کد به هوش مصنوعی، الگوهای مخفی‌کاری (Secrets) را با RegEx محلی شناسایی کنید:

```python
import re

def scan_secrets_locally(code_content):
    patterns = {
        "GitHub Token": r"gh[p_][a-zA-Z0-9]{36}",
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "Private Key": r"-----BEGIN PRIVATE KEY-----"
    }
    found_risks = []
    for name, pattern in patterns.items():
        if re.search(pattern, code_content):
            found_risks.append({"category": "Security", "severity": "High", "description": f"Detected potential {name} leak!"})
    return found_risks
```
این تابع را می‌توان به راحتی در متد `analyze_code` در فایل `core/ai_engine.py` اضافه کرد تا پیش از تحلیل هوش مصنوعی، کلیدهای حساس لو رفته بلافاصله شناسایی شوند.
