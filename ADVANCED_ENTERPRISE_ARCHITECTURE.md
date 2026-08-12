# معماری پیشرفته و انترپرایز: امنیت افزونه‌ها، احراز هویت OIDC و اتوماسیون تست در CI/CD

این سند سه بخش حیاتی از توسعه در سطح Enterprise را پوشش می‌دهد:
1. **ایمن‌سازی و ایزوله‌سازی لودر افزونه‌ها (Plugin Sandboxing)**
2. **یکپارچه‌سازی پروتکل OIDC با Keycloak و Azure AD**
3. **اتوماسیون اجرای تست‌های واحد هوش مصنوعی در CI/CD و نمایش در دسکتاپ**

---

## ۱. ایمن‌سازی و ایزوله‌سازی لودر افزونه‌ها (Plugin Sandboxing)

برای جلوگیری از اجرای کدهای مخرب توسط پلاگین‌های شخص ثالث (Third-Party Plugins) در محیط دسکتاپ، استفاده از محدودسازی دسترسی سیستم‌عامل (Restricted Restricted Execution / AST Analysis) و اجرای هر پلاگین در یک روند جداگانه (Subprocess / IPC) توصیه می‌شود.

### بررسی محتوای AST پیش از لود کردن پلاگین:
پیش از اجرای فایل پایتون پلاگین، ساختار آن با کتابخانه `ast` بررسی می‌شود تا از عدم وجود توابع خطرناک مانند `os.system`, `subprocess`, یا `eval` اطمینان حاصل شود:

```python
import ast

class PluginSecurityValidator(ast.NodeVisitor):
    def __init__(self):
        self.forbidden_modules = {"os", "subprocess", "sys", "shutil", "socket"}
        self.forbidden_functions = {"eval", "exec", "open", "compile"}
        self.violations = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in self.forbidden_modules:
                self.violations.append(f"Forbidden module import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in self.forbidden_modules:
            self.violations.append(f"Forbidden import from module: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in self.forbidden_functions:
            self.violations.append(f"Forbidden function call: {node.func.id}")
        self.generic_visit(node)

def validate_plugin_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)
    validator = PluginSecurityValidator()
    validator.visit(tree)
    return validator.violations
```

---

## ۲. یکپارچه‌سازی پروتکل OIDC با Keycloak و Azure AD

برای اتصال به سامانه‌های هویت‌سنجی سازمانی مانند **Keycloak** یا **Microsoft Azure AD (Entra ID)**، کتابخانه استاندارد `requests_oauthlib` یا پیکربندی مستقیم OIDC Discovery Endpoint استفاده می‌شود.

### نمونه کد پیکربندی و احراز هویت OIDC:
```python
from requests_oauthlib import OAuth2Session
import webbrowser

class EnterpriseOIDCAuth:
    def __init__(self, provider="keycloak"):
        if provider == "keycloak":
            self.client_id = "ai-code-reviewer-desktop"
            self.base_url = "https://sso.yourcompany.com/realms/enterprise"
            self.auth_url = f"{self.base_url}/protocol/openid-connect/auth"
            self.token_url = f"{self.base_url}/protocol/openid-connect/token"
        else:  # Azure AD
            self.tenant_id = "your-tenant-guid"
            self.client_id = "azure-client-id"
            self.auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
            self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        self.redirect_uri = "http://localhost:8085/callback"

    def get_authorization_url(self):
        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=["openid", "profile", "email"])
        authorization_url, state = oauth.authorization_url(self.auth_url)
        return authorization_url, state

    def fetch_token_from_callback(self, authorization_response_url):
        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri)
        token = oauth.fetch_token(
            self.token_url,
            authorization_response=authorization_response_url,
            include_client_id=True,
            client_secret="your-client-secret"  # در صورت نیاز برای کلاینت‌های محرمانه
        )
        return token
```

---

## ۳. اتوماسیون اجرای تست‌های واحد در CI/CD و نمایش در دسکتاپ

برای اینکه کدهای تست تولیدشده توسط هوش مصنوعی به‌طور خودکار در پایپ‌لاین گیت‌هاب اجرا شوند و نتایج آن در رابط کاربری دسکتاپ قابل مشاهده باشد، فایل تنظیمات CI/CD گسترش می‌یابد.

### افزودن مرحله تست به `.github/workflows/build.yml`:
```yaml
    - name: Run AI-Generated Unit Tests
      run: |
        pip install pytest pytest-json-report
        pytest --json-report --json-report-file=test_report.json || true
    - name: Upload Test Report Artifact
      uses: actions/upload-artifact@v4
      with:
        name: test-report
        path: test_report.json
```

### بارگذاری و نمایش نتایج در اپلیکیشن دسکتاپ (PySide6):
در بخش دسکتاپ، کاربر می‌تواند فایل گزارش تست (`test_report.json`) را بارگذاری کرده و وضعیت موفقیت یا شکست تست‌ها را در جدول مشاهده کند:

```python
import json
from PySide6.QtWidgets import QTableWidgetItem

def load_test_report(self, filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tests = data.get("tests", [])
        self.issues_table.setRowCount(len(tests))
        for row, test in enumerate(tests):
            nodeid = test.get("nodeid", "Test")
            outcome = test.get("outcome", "passed")
            duration = str(test.get("duration", 0.0))
            
            self.issues_table.setItem(row, 0, QTableWidgetItem(nodeid))
            self.issues_table.setItem(row, 1, QTableWidgetItem(outcome))
            self.issues_table.setItem(row, 2, QTableWidgetItem(duration))
            self.log(f"Loaded test result: {nodeid} -> {outcome}")
    except Exception as e:
        self.log(f"Failed to load test report: {str(e)}")
```
