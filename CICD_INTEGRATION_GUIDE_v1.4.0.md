# راهنمای یکپارچه‌سازی CI/CD و مشخصات API (نسخه v1.4.0)

**پروژه:** AI-Code-Reviewer Enterprise  
**ماژول هدف:** موتور تحلیل هوشمند قابل‌بهره‌برداری بودن آسیب‌پذیری‌ها (`EnterpriseExploitabilityEngine`)  
**نسخه:** v1.4.0  
**نویسنده:** Manus AI

---

## ۱. مقدمه و معماری یکپارچه‌سازی

ماژول `EnterpriseExploitabilityEngine` در نسخه **v1.4.0** به منظور حذف هشدارهای کاذب (False Positives) در اسکن پکیج‌های شخص ثالث طراحی شده است. این موتور بررسی می‌کند که آیا توابع یا نمادهای آسیب‌پذیر (`Vulnerable Symbols`) در کدهای مخزن کاربر فراخوانی شده‌اند یا خیر.

---

## ۲. مشخصات فنی API (Python Interface)

```python
from core.ai_engine_v140_features import EnterpriseExploitabilityEngine

# راه‌اندازی موتور
engine = EnterpriseExploitabilityEngine(cve_database_path="rules/cve_advisories.json")

# فراخوانی متد ارزیابی
result = engine.analyze_dependency_exploitability(
    dependency_name="requests",
    current_version="2.28.0",
    used_symbols=["requests.packages.urllib3"]
)

print(result)
```

### ساختار خروجی (JSON Response Schema):
```json
{
  "dependency": "requests",
  "version": "2.28.0",
  "cve": "CVE-2023-32681",
  "severity": "High",
  "vulnerable_symbols_detected": ["requests.packages.urllib3"],
  "is_exploitable_in_context": true,
  "recommended_action": "Immediate patch required"
}
```

---

## ۳. نمونه اسکریپت GitHub Actions برای پایپ‌لاین CI/CD

برای اجرای خودکار تحلیل بهره‌برداری در هر Commit یا Pull Request، فایل `.github/workflows/exploit_scan.yml` به شکل زیر تنظیم می‌شود:

```yaml
name: AI-Code-Reviewer Exploitability Scan

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  sast-exploit-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run v1.4.0 Exploitability Check
        run: |
          python3 -c '
          from core.ai_engine_v140_features import EnterpriseExploitabilityEngine
          engine = EnterpriseExploitabilityEngine()
          res = engine.analyze_dependency_exploitability("requests", "2.28.0", ["requests.packages.urllib3"])
          print("Scan Result:", res)
          if res.get("is_exploitable_in_context"):
              print("CRITICAL: Vulnerable code path invoked!")
              exit(1)
          '
```

---
*این مستند راهنمای استاندارد تیم‌های DevOps برای استقرار ابزار در محیط‌های تولیدی سازمانی است.*
