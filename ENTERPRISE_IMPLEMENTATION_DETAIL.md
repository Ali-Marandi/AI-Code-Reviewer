# مستند معماری و پیاده‌سازی پیشرفته AI-Code-Reviewer Enterprise

این سند جزئیات فنی سه ویژگی پیشرفته اینترپرایز شامل **مدیریت حافظه و کشینگ (Context Caching)**، **اسکن امنیتی محلی (Local SAST)**، و **سیستم گزارش‌گیری و انطباق (Audit Logging & Compliance)** را تشریح می‌کند.

---

## ۱. مدیریت حافظه و Context Caching در نسخه دسکتاپ

برای جلوگیری از مصرف بی‌رویه‌ی رم (RAM) هنگام بررسی پروژه‌های بزرگ و کاهش تعداد درخواست‌های تکراری به مدل‌های هوش مصنوعی (و در نتیجه کاهش هزینه‌ها و افزایش سرعت)، سیستم **Persistent Context Caching** پیاده‌سازی می‌شود.

### معماری کشینگ محلی با SQLite:
استفاده از پایگاه داده سبک SQLite برای ذخیره نتایج تحلیل فایل‌ها بر اساس هش محتوای کد (SHA-256 Hash):

```python
import sqlite3
import hashlib
import json

class ReviewCache:
    def __init__(self, db_path="review_cache.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    file_hash TEXT PRIMARY KEY,
                    review_result TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get_cached_review(self, code_content):
        file_hash = hashlib.sha256(code_content.encode('utf-8')).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute("SELECT review_result FROM cache WHERE file_hash = ?", (file_hash,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

    def set_cached_review(self, code_content, review_data):
        file_hash = hashlib.sha256(code_content.encode('utf-8')).hexdigest()
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO cache (file_hash, review_result) VALUES (?, ?)",
                (file_hash, json.dumps(review_data))
            )
```

---

## ۲. ماژول اسکن امنیتی محلی (Local SAST)

برای شناسایی سریع آسیب‌پذیری‌های بحرانی و کلیدهای مخفی (Secrets & PII) پیش از ارسال کد به هوش مصنوعی، ماژول `core/security_scanner.py` به صورت لوکال اجرا می‌شود.

### پیاده‌سازی اسکنر محلی:
```python
import re

class LocalSecurityScanner:
    def __init__(self):
        self.patterns = {
            "Hardcoded GitHub Token": r"gh[p_][a-zA-Z0-9]{36}",
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "Private Key Block": r"-----BEGIN PRIVATE KEY-----",
            "Potential SQL Injection (exec/eval)": r"\b(eval|exec)\s*\(",
            "Hardcoded Password Variable": r"(password|secret|api_key)\s*=\s*['\"][^'\"]+['\"]"
        }

    def scan_code(self, code_text):
        issues = []
        lines = code_text.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            for risk_name, pattern in self.patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "line": line_num,
                        "severity": "High" if "Token" in risk_name or "Key" in risk_name else "Medium",
                        "category": "Security",
                        "description": f"Local SAST Alert: {risk_name} detected.",
                        "suggestion": "Remove hardcoded credentials or unsafe execution functions. Use environment variables."
                    })
        return issues
```

---

## ۳. ماژول گزارش‌گیری پیشرفته (Audit Logging) و انطباق سازمانی

برای سازمان‌ها و تیم‌های بزرگ، ثبت تمامی رویدادها، بازبینی‌ها و اقدامات کاربران (Audit Trail) جهت انطباق با استانداردهای امنیتی (مانند SOC2 و ISO 27001) یک ضرورت است.

### پیاده‌سازی سیستم لاگینگ سازمانی (`core/audit_logger.py`):
```python
import logging
import os
from datetime import datetime

class AuditLogger:
    def __init__(self, log_file="enterprise_audit.log"):
        self.logger = logging.getLogger("EnterpriseAudit")
        self.logger.setLevel(logging.INFO)
        
        # فرمت لاگ سازگار با استانداردهای انطباق
        formatter = logging.Formatter('%(asctime)s | [%(levelname)s] | User: %(username)s | Action: %(action)s | Details: %(message)s')
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)

    def log_event(self, username, action, details):
        extra = {'username': username, 'action': action}
        self.logger.info(details, extra=extra)
```

با استفاده از این ماژول‌ها، نرم‌افزار دسکتاپ `AI-Code-Reviewer Enterprise` از نظر سرعت، امنیت محلی و انطباق سازمانی کاملاً در سطح ابزارهای پیشرو تجاری قرار می‌گیرد.
