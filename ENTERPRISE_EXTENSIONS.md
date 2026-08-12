# معماری و پیاده‌سازی قابلیت‌های پیشرفته Enterprise در AI-Code-Reviewer

این سند نحوه پیاده‌سازی سه قابلیت کلیدی شامل **تولید خودکار تست واحد (AI Unit Test Generation)**، **احراز هویت سازمانی (SSO / LDAP)**، و **معماری افزونه‌پذیر (Plugin Architecture)** را شرح می‌دهد.

---

## ۱. ماژول تولید خودکار تست واحد (AI Unit Test Generation)

برای افزایش پوشش کد (Code Coverage) و اتوماسیون فرآیند QA، این ماژول کدهای سورس را دریافت کرده و تست‌های استاندارد (مثل `pytest` برای پایتون یا `Jest` برای جاوااسکریپت) را تولید می‌کند.

### پیاده‌سازی در هسته هوش مصنوعی (`core/test_generator.py`):
```python
class AITestGenerator:
    def __init__(self, ai_engine):
        self.ai = ai_engine

    def generate_unit_tests(self, code_content, file_path, framework="pytest"):
        system_prompt = (
            f"You are an expert QA engineer. Generate comprehensive unit tests using {framework} "
            f"for the provided source code file ({file_path}). "
            "Ensure edge cases, error handling, and mock objects are covered. "
            "Return ONLY the executable test code in Markdown code blocks."
        )
        user_prompt = f"Source Code:\n{code_content}"
        
        # استفاده از موتور هوش مصنوعی موجود
        review = self.ai.client.chat.completions.create(
            model=self.ai.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        content = review.choices[0].message.content
        if "```python" in content:
            content = content.split("```python")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return content
```

---

## ۲. مکانیزم احراز هویت سازمانی (SSO / LDAP / OIDC)

برای سازمان‌هایی که از دایرکتوری‌های مرکزی (مانند Active Directory یا Okta / Keycloak) استفاده می‌کنند، اپلیکیشن دسکتاپ می‌تواند از طریق پروتکل **OIDC (OpenID Connect)** با مرورگر سیستم احراز هویت کند.

### جریان احراز هویت در دسکتاپ:
1. کاربر روی دکمه "Login with Enterprise SSO" کلیک می‌کند.
2. اپلیکیشن یک سرور لوکال موقت (`http://localhost:8085/callback`) راه‌اندازی می‌کند.
3. مرورگر پیش‌فرض سیستم برای ورود به پنل سازمانی باز می‌شود.
4. پس از ورود موفق، توکن JWT به اپلیکیشن دسکتاپ بازگردانده شده و نشست کاربر امن می‌شود.

```python
import http.server
import socketserver
import webbrowser
import threading
import urllib.parse

class SSOLoginHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'code' in query_components:
            auth_code = query_components['code'][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>SSO Authentication Successful! You can close this window.</h1>")
            # انتقال توکن به پنجره اصلی برنامه
            print(f"Received SSO Authorization Code: {auth_code}")
        else:
            self.send_response(400)
            self.end_headers()

def start_sso_listener():
    port = 8085
    server = socketserver.TCPServer(("127.0.0.1", port), SSOLoginHandler)
    threading.Thread(target=server.handle_request, daemon=True).start()
    webbrowser.open(f"https://sso.enterprise.com/oauth/authorize?client_id=ai_reviewer&redirect_uri=http://localhost:{port}/callback&response_type=code")
```

---

## ۳. معماری افزونه‌پذیری (Plugin Architecture)

برای اینکه تیم‌های مهندسی بتوانند قوانین بررسی کد دلخواه یا مانیتورینگ سفارشی خود را به نرم‌افزار اضافه کنند، یک معماری مبتنی بر پکیج‌های پلاگین در مسیر `/plugins` طراحی شده است.

### تعریف اینترفیس پایه پلاگین (`core/plugin_base.py`):
```python
class BasePlugin:
    def __init__(self):
        self.name = "Base Plugin"
        self.version = "1.0.0"

    def run_audit(self, code_content, file_path):
        """باید توسط پلاگین‌های سفارشی پیاده‌سازی شود"""
        raise NotImplementedError
```

### لودر پویا برای بارگذاری پلاگین‌ها در زمان اجرا:
```python
import os
import importlib.util

def load_plugins_from_directory(plugin_dir="plugins"):
    plugins = []
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)
        return plugins

    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            filepath = os.path.join(plugin_dir, filename)
            spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    plugins.append(attr())
    return plugins
```

با این معماری ماژولار، هر تیمی می‌تواند پلاگین‌های اختصاصی خود را نوشته و بدون تغییر در سورس‌کد اصلی، قابلیت‌های جدیدی به نسخه دسکتاپ اضافه کند.
