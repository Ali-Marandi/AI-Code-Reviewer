# مستند جامع معماری: تله‌متری ابری، رمزنگاری E2EE و موتور قوانین سفارشی

این سند راهبردهای مهندسی برای پیاده‌سازی سه قابلیت پیشرفته در نسخه اینترپرایز شامل **مانیتورینگ ابری (Cloud Telemetry)**، **رمزنگاری سرتاسری (End-to-End Encryption)**، و **سیستم قوانین سفارشی تمیزی کد (Custom Linting Rules)** را ارائه می‌دهد.

---

## ۱. مانیتورینگ عملکرد و لاگ‌برداری ابری (Cloud Telemetry)

برای ردیابی خطاهای نرم‌افزار دسکتاپ، بررسی پایداری سیستم و اندازه‌گیری کارایی هوش مصنوعی در محیط سازمانی، پلتفرم‌های مانیتورینگ استاندارد مانند **Sentry** (برای ردیابی خطاها) و **OpenTelemetry** (برای ردیابی عملکرد) یکپارچه می‌شوند.

### پیاده‌سازی مانیتورینگ خطاها با Sentry:
```python
import sentry_sdk

def init_telemetry():
    sentry_sdk.init(
        dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
        traces_sample_rate=1.0,
        environment="enterprise-production",
        release="ai-code-reviewer@1.0.2"
    )
```

هرگونه خطای شبکه، خطای احراز هویت یا خرابی در تحلیل هوش مصنوعی به صورت خودکار و امن (بدون ارسال کدهای سورس حساس) به سرور تله‌متری سازمان ارسال می‌شود.

---

## ۲. رمزنگاری سرتاسری (End-to-End Encryption - E2EE)

برای ذخیره‌سازی توکن‌های گیت‌هاب، کلیدهای API مدل‌های هوش مصنوعی و تنظیمات حساس در دیسک محلی کاربر، از کتابخانه رمزنگاری پیشرفته `cryptography` با استاندارد **AES-256-GCM** استفاده می‌شود.

### پیاده‌سازی ماژول رمزنگاری محلی (`core/secure_storage.py`):
```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecureStorage:
    def __init__(self, master_password: str):
        # مشتق‌سازی کلید از رمز عبور اصلی کاربر (Master Password)
        self.key = hashlib.pbkdf2_hmac('sha256', master_password.encode(), b'enterprise_salt', 100000)
        self.aesgcm = AESGCM(self.key)

    def encrypt_data(self, plaintext: str) -> bytes:
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        return nonce + ciphertext

    def decrypt_data(self, encrypted_data: bytes) -> str:
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')
```

---

## ۳. سیستم بررسی تطابق با قوانین تمیزی کد (Custom Linting Rules)

برای اعمال استانداردهای داخلی سازمان (مانند حداکثر طول توابع، اجباری بودن Docstring، یا منع استفاده از کلمات کلیدی خاص)، یک موتور قوانین سفارشی بر پایه تحلیل AST پایتون پیاده‌سازی می‌شود.

### نمونه موتور بررسی قوانین سفارشی (`core/custom_linter.py`):
```python
import ast

class CustomCleanCodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []
        self.max_function_lines = 30

    def visit_FunctionDef(self, node):
        # بررسی طول تابع (قانون سادگی و تمیزی)
        if node.end_lineno and (node.end_lineno - node.lineno > self.max_function_lines):
            self.violations.append({
                "line": node.lineno,
                "severity": "Medium",
                "category": "Style",
                "description": f"Function '{node.name}' is too long ({node.end_lineno - node.lineno} lines). Max allowed is {self.max_function_lines}.",
                "suggestion": "Refactor the function into smaller, modular helper functions."
            })
        
        # بررسی وجود Docstring
        if not ast.get_docstring(node):
            self.violations.append({
                "line": node.lineno,
                "severity": "Low",
                "category": "Style",
                "description": f"Function '{node.name}' lacks a docstring.",
                "suggestion": "Add a descriptive docstring explaining arguments and return values."
            })
        
        self.generic_visit(node)

def run_custom_lint(code_text):
    try:
        tree = ast.parse(code_text)
        visitor = CustomCleanCodeVisitor()
        visitor.visit(tree)
        return visitor.violations
    except SyntaxError as e:
        return [{
            "line": e.lineno or 1,
            "severity": "High",
            "category": "Bug",
            "description": f"Syntax Error: {e.msg}",
            "suggestion": "Fix syntax error before running clean code audit."
        }]
```

این موتور به همراه تحلیل هوش مصنوعی و اسکنر SAST محلی، کیفیت و انطباق کد را به بالاترین سطح استاندارد تجاری می‌رساند.
