# یادداشت‌های پژوهش قابلیت‌های Enterprise

## منابع و یافته‌های تأییدشده

| قابلیت پیشنهادی | یافته قابل استناد | منبع |
|---|---|---|
| خروجی SARIF | OASIS، SARIF را قالب استاندارد خروجی ابزارهای تحلیل ایستا تعریف می‌کند. | https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html |
| هم‌زیستی با GitHub Code Scanning | GitHub امکان آپلود SARIF تولیدشده خارج از GitHub و مشاهده Alertهای ابزار ثالث در مخزن را فراهم می‌کند؛ برای چند فایل/تحلیل باید دسته‌بندی یا شناسه اجرای یکتا رعایت شود. | https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file |
| موتور قواعد سفارشی | Semgrep قواعد سفارشی را برای یافتن ضعف‌های امنیتی، نقض‌های Secure Coding و خطاها معرفی می‌کند؛ این قواعد می‌توانند منطق تطبیق، پیام و اصلاح پیشنهادی داشته باشند. | https://docs.semgrep.dev/writing-rules/overview |

## نتیجه اولویت‌بندی اولیه

1. **Custom Rule Engine با فایل JSON محلی و اعتبارسنجی schema ساده**: سریع، Local-first و مناسب برای سیاست‌های سازمانی؛ قابلیت اتصال به `run_local_sast` موجود را دارد.
2. **SARIF 2.1.0 Export**: خروجی استاندارد قابل استفاده در CI/CD و GitHub Code Scanning؛ ارزش Enterprise ملموس بدون وابستگی ابری.
3. **Historical Findings / Technical Debt Trend در SQLite**: بستر عملیاتی لازم برای گزارش KPI و Trend، با حفظ Local-first؛ نیازمند محدود کردن حجم و مدیریت تاریخچه است.
4. **Multi-language regex detectors (Java/Go/Rust) در Rule Engine**: دامنه تحلیل فعلی UI را عملیاتی‌تر می‌کند، اما باید به قواعد تست‌شده محدود باشد تا ادعای تحلیل نحوی عمیق نادرست ایجاد نشود.

## محدودیت‌های طراحی

- Rule Engine فقط داده JSON را می‌خواند؛ از اجرای کد، Expression، Template یا Plugin برای قواعد جلوگیری می‌شود.
- SARIF باید شامل ruleId، message، level، artifact URI و startLine باشد تا ابزارهای پایین‌دستی بتوانند یافته را محل‌یابی کنند.
- هر نتیجه تاریخی باید یک fingerprint پایدار و تاریخ مشاهده داشته باشد تا شمارش تکراری و Trend تحریف نشود.
- قواعد سفارشی باید فقط با Regexهای محدود و قابل اعتبارسنجی پشتیبانی شوند؛ خطاهای Regex باید بدون توقف کل اسکن گزارش شوند.
