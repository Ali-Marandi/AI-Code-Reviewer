# مدیریت پروانه‌ها، تست‌های خودکار و مستندسازی جامع AI-Code-Reviewer Enterprise

این سند آخرین بخش از پلتفرم تجاری (Enterprise) را تکمیل می‌کند و شامل مکانیزم مدیریت متمرکز پروانه‌ها، تست‌های واحد خودکار و استانداردهای مستندسازی است.

---

## ۱. مدیریت متمرکز پروانه‌ها (License Management) و استقرار ابری

برای سازمان‌ها و شرکت‌های بزرگ که تعداد زیادی کاربر دسکتاپ دارند، سیستم مدیریت پروانه مبتنی بر توکن‌های دیجیتال امضاشده (JWT / RSA Signature) پیاده‌سازی می‌شود.

### الف. ساختار سرور صدور پروانه (License Server):
سرور ابری وظیفه اعطای مجوز استفاده به ازای شناسه سخت‌افزاری دستگاه (Machine Fingerprint) را بر عهده دارد:
- **اعتبار سنجی دوره‌ای:** نرم‌افزار دسکتاپ هر ۷ روز یک‌بار به سرور ابری متصل شده و اعتبار پروانه را تمدید می‌کند.
- **امضای دیجیتال:** فایل لایسنس با کلید خصوصی سرور امضا می‌شود و کلاینت با کلید عمومی آن را اعتبارسنجی می‌کند تا از جعل جلوگیری شود.

---

## ۲. تست‌های واحد و اتوماسیون (Unit Testing)

برای تضمین پایداری ماژول‌های امنیتی (Local SAST)، رمزنگاری (E2EE) و موتور تمیزی کد (Custom Linter)، تست‌های خودکار با استفاده از فریم‌ورک `pytest` در پوشه `/tests` پیاده‌سازی شده‌اند.

### نمونه اسکریپت تست واحد (`tests/test_enterprise.py`):
```python
import pytest
from core.security_scanner import LocalSecurityScanner
from core.custom_linter import run_custom_lint
from core.secure_storage import SecureStorage

def test_local_sast_secret_detection():
    scanner = LocalSecurityScanner()
    code = "api_key = 'ghp_REDACTED_EXAMPLE_TOKENAB'\n"
    issues = scanner.scan_code(code)
    assert len(issues) > 0
    assert issues[0]['category'] == 'Security'

def test_custom_linter_long_function():
    # ساخت یک تابع بسیار طولانی برای تست قانون تمیزی کد
    long_func = "def very_long_func():\n" + "\n".join([f"    x_{i} = {i}" for i in range(40)]) + "\n    pass"
    violations = run_custom_lint(long_func)
    assert any("too long" in v['description'] for v in violations)

def test_secure_storage_encryption():
    storage = SecureStorage("MasterPassword123!")
    secret = "my_super_secret_token"
    encrypted = storage.encrypt_data(secret)
    decrypted = storage.decrypt_data(encrypted)
    assert decrypted == secret
```

---

## ۳. راهنمای کاربری (User Manual) و مستندات توسعه‌دهندگان (Developer Docs)

### الف. راهنمای کاربری (User Manual Summary):
1. **نصب و راه‌اندازی:** دانلود فایل `AI-Code-Reviewer-Enterprise.exe` از بخش Releases گیت‌هاب و اجرای آن.
2. **احراز هویت سازمانی:** ورود با حساب سازمانی از طریق دکمه Enterprise SSO (پشتیبانی از Keycloak و Azure AD).
3. **انتخاب مخزن و بازبینی:** انتخاب مخزن گیت‌هاب از لیست، انتخاب Pull Request مورد نظر و کلیک روی دکمه "Run AI Enterprise Review".
4. **اعمال اصلاحات:** مشاهده جدول یافته‌ها و استفاده از قابلیت اصلاح تک‌کلیکی (One-Click Patch).

### ب. راهنمای توسعه‌دهندگان (Developer Docs Summary):
1. **ساختار پروژه:** معماری ماژولار شامل `core/` (هوش مصنوعی، اسکنرها، امنیت) و `ui/` (رابط کاربری PySide6 و Multi-threading).
2. **توسعه افزونه‌های سفارشی:** استفاده از کلاس پایه `BasePlugin` و لودر امن AST برای توسعه و افزودن ماژول‌های تحلیلی جدید بدون نیاز به تغییر سورس اصلی.
3. **پایپ‌لاین CI/CD:** ساخت خودکار بسته اجرایی ویندوز با اتریبیوت‌های امنیتی گیت‌هاب و آپلود مستقیم در Releases.
