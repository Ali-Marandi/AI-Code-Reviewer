# AI-Code-Reviewer Enterprise

**AI-Code-Reviewer Enterprise** یک ابزار Local-first برای بازبینی کد، تحلیل ایستای امنیتی و مدیریت یافته‌ها در جریان GitHub است. نسخه v1.0.4 قابلیت اعمال قواعد سازمانی از طریق Rule Pack محلی، خروجی استاندارد SARIF و مشاهده روند محلی یافته‌ها را اضافه می‌کند.

> این ابزار تصمیم امنیتی نهایی یا جایگزین بازبینی انسانی نیست. هر یافته، به‌ویژه یافته‌های تولیدشده توسط AI یا Regex، باید در بافت کد و مدل تهدید سازمان بازبینی شود.

## قابلیت‌های کلیدی

| قابلیت | شرح |
|---|---|
| تحلیل AI و Local SAST | بررسی خطا، ریسک امنیتی، وابستگی‌ها و نشانه‌های ساده Bug Prediction؛ در صورت نبود سرویس AI، کنترل‌های محلی ادامه پیدا می‌کنند. |
| Rule Pack محلی و امن | بارگذاری فایل JSON با schema نسخه‌دار و Regexهای اعتبارسنجی‌شده؛ Rule Pack هیچ کد، Plugin یا subprocess اجرا نمی‌کند. |
| دامنه چندزبانه کنترل‌شده | Rule Pack پیش‌فرض، فایل‌های Python، JavaScript/TypeScript، Java، Go و Rust را بر مبنای الگوهای قابل ممیزی بررسی می‌کند. این قابلیت جایگزین parser یا compiler اختصاصی زبان‌ها نیست. |
| خروجی SARIF 2.1.0 | ذخیره یافته‌ها به‌صورت فایل محلی سازگار با جریان‌های Code Scanning/CI. SARIF فرمت استاندارد خروجی ابزارهای تحلیل ایستا است.[1] |
| Trend محلی یافته‌ها | ذخیره metadata اسکن و fingerprint هش‌شده برای روند ۳۰ روزه؛ متن کد منبع، Secret و snippet در تاریخچه ذخیره نمی‌شود. |
| رابط دسکتاپ ویندوز | مرور مخزن و Pull Request، جدول یافته‌ها با Rule ID، انتخاب Rule Pack محلی، Export SARIF و صفحه Findings Trend. |
| CI/CD | اجرای CLI روی Pull Request و تولید اختیاری فایل SARIF برای مصرف مستقل در خط لوله. GitHub امکان بارگذاری SARIF ابزارهای ثالث را در Code Scanning فراهم می‌کند.[2] |

## نصب

### نسخه دسکتاپ

فایل `.exe` یا `.msi` منتشرشده را از [GitHub Releases](https://github.com/Ali-Marandi/AI-Code-Reviewer/releases) دریافت کنید. برای دریافت یا اجرای نسخه داخلی، از فرایند تأییدشده سازمان استفاده کنید.

### توسعه محلی

```bash
git clone https://github.com/Ali-Marandi/AI-Code-Reviewer.git
cd AI-Code-Reviewer
python -m pip install -r requirements.txt
python app.py
```

## استفاده در رابط کاربری

پس از ورود توکن GitHub در Settings، یک مخزن و Pull Request را انتخاب کنید. در همان صفحه Review، یافته‌ها شامل **Severity**، **Rule ID**، دسته‌بندی، توضیح و پیشنهاد نمایش داده می‌شوند. دکمه **Export SARIF** فقط فایل را روی دستگاه کاربر ذخیره می‌کند؛ داده‌ای را به GitHub یا سرویس ثالث بارگذاری نمی‌کند.

در Settings می‌توان مسیر Rule Pack JSON را انتخاب کرد. فقط Rule Packهای JSON معتبر با `schema_version: 1` پذیرفته می‌شوند. Rule یا Regex نامعتبر، به‌عنوان Notice ثبت می‌شود و Local SAST را متوقف نمی‌کند.

## ساختار Rule Pack

Rule Pack پیش‌فرض در مسیر `rules/enterprise_default_rules.json` قرار دارد. هر Rule فقط metadata و Regex محدود دارد.

```json
{
  "schema_version": 1,
  "name": "Example Organisation Policy",
  "version": "1.0.0",
  "rules": [
    {
      "id": "ORG-PY-NO-SHELL-TRUE",
      "pattern": "subprocess\\.(?:run|call)\\s*\\([^\\n]*shell\\s*=\\s*True",
      "languages": ["python"],
      "severity": "High",
      "category": "Security",
      "description": "shell=True requires a security review.",
      "suggestion": "Use fixed command arguments and validate input.",
      "ignore_case": false
    }
  ]
}
```

| فیلد | الزام | توضیح |
|---|---|---|
| `schema_version` | بله | در v1.0.4 باید مقدار `1` باشد. |
| `id` | بله | شناسه یکتای Rule برای ممیزی، Trend و SARIF. |
| `pattern` | بله | Regex با سقف طول و اعتبارسنجی در زمان بارگذاری. |
| `languages` | بله | فهرست زبان‌های پشتیبانی‌شده یا `all`. |
| `severity` | بله | یکی از `Critical`، `High`، `Medium`، `Low` یا `Info`. |
| `category`، `description`، `suggestion` | بله | داده نمایش، Triage و راهنمای بازبینی انسانی. |
| `ignore_case` | خیر | Boolean برای اجرای Regex بدون حساسیت به حروف. |

## CLI و SARIF در CI/CD

اجرای CLI علاوه بر ارسال گزارش Pull Request، می‌تواند یک فایل SARIF محلی بسازد. مسیر خروجی اختیاری است و باید به مرحله مجزای CI برای Archive یا Upload داده شود.

```bash
python app.py \
  --cli \
  --token "$GITHUB_TOKEN" \
  --owner OWNER \
  --repo REPOSITORY \
  --pr 123 \
  --rule-pack rules/enterprise_default_rules.json \
  --sarif-output artifacts/ai-code-reviewer.sarif
```

برای ارسال SARIF به GitHub Code Scanning، باید آن را در Workflow و با مجوزهای درست بارگذاری کنید. GitHub مستندات رسمی برای آپلود فایل SARIF و استفاده از `github/codeql-action/upload-sarif` دارد.[2] پیش از فعال‌سازی، قابلیت Code Security مخزن، سیاست حریم خصوصی و مجوز `security-events: write` را بررسی کنید.

## حریم خصوصی و محدودیت‌ها

| موضوع | رفتار v1.0.4 |
|---|---|
| Rule Pack | فقط از فایل JSON محلی خوانده می‌شود؛ امکان اجرای اسکریپت یا Plugin وجود ندارد. |
| Trend History | زمان اسکن، هش مسیر، تعداد یافته، شدت، شناسه Rule و fingerprint هش‌شده نگهداری می‌شود. |
| کد و Secret | در جدول تاریخچه SQLite ذخیره نمی‌شوند. در Cache بازبینی، خروجی تحلیل نگهداری می‌شود؛ مسیر Cache باید با سیاست نگهداشت داده سازمان هماهنگ باشد. |
| SARIF | فایل محلی شامل metadata و متن یافته است و ممکن است برای داده حساس در ابزار پایین‌دستی نیازمند کنترل دسترسی باشد. |
| خروجی AI | یافته AI قطعی نیست؛ قبل از اصلاح یا گزارش بیرونی، بازبینی انسانی لازم است. |

## آزمون

```bash
python -m py_compile core/ai_engine.py ui/main_window.py app.py
python -m unittest discover -s tests -v
```

## مجوز

Commercial License — All Rights Reserved.

## منابع

[1]: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html "OASIS — Static Analysis Results Interchange Format (SARIF) Version 2.1.0"
[2]: https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file "GitHub Docs — Uploading a SARIF file to GitHub"
