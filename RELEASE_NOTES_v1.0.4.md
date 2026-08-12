# یادداشت انتشار — v1.0.4

**AI-Code-Reviewer Enterprise**
**نوع انتشار:** قابلیت Enterprise و بهبود قابلیت ادغام
**وضعیت:** آماده برای انتشار کنترل‌شده پس از تأیید CI ویندوز و بازبینی Release Owner

## خلاصه

v1.0.4 سه توانمندی Enterprise را به مسیر Local-first محصول اضافه می‌کند: Rule Packهای سازمانی مبتنی بر JSON، خروجی محلی SARIF 2.1.0 و تاریخچه کمینه‌داده یافته‌ها در SQLite. این نسخه به‌گونه‌ای طراحی شده است که قابلیت اعمال سیاست سازمانی و تبادل یافته با ابزارهای تحلیل موجود را افزایش دهد، بدون اینکه ارسال خودکار کد یا یافته به سرویس جدیدی انجام شود.

SARIF یک استاندارد OASIS برای خروجی ابزارهای تحلیل ایستا است و GitHub می‌تواند فایل‌های SARIF ابزارهای ثالث را در جریان Code Scanning دریافت کند.[1] [2] قابلیت Export در v1.0.4 فقط فایل محلی می‌سازد؛ Upload یا انتشار خارجی، یک مرحله جداگانه و نیازمند پیکربندی صریح CI است.

## قابلیت‌های جدید

| حوزه | تغییر | اثر عملیاتی |
|---|---|---|
| Custom Rule Engine | بارگذاری Rule Pack JSON با `schema_version: 1`، شناسه Rule، Regex، زبان، شدت، دسته‌بندی، توضیح و پیشنهاد | اعمال کنترل‌های Secure Coding سازمانی بدون اجرای Plugin یا کد سفارشی |
| پشتیبانی زبانی کنترل‌شده | Rule Pack پیش‌فرض برای Python، JavaScript/TypeScript، Java، Go و Rust | پوشش قابل ممیزی الگوهای مشخص؛ نه ادعای تحلیل نحوی کامل برای تمام زبان‌ها |
| SARIF Export | ساخت SARIF 2.1.0 از یافته‌های Review در UI و CLI | استفاده در Artifactهای CI و مسیرهای Code Scanning پشتیبانی‌شده |
| Trend محلی | ذخیره metadata اسکن و fingerprint هش‌شده در SQLite | مشاهده اسکن، یافته‌ها، یافته‌های High/Critical و fingerprintهای یکتا در ۳۰ روز |
| رابط کاربری | Rule ID در جدول یافته، انتخاب Rule Pack، Export SARIF و صفحه Findings Trend | Triage روشن‌تر و مشاهده روند، بدون نمایش کد در تاریخچه |
| CLI/CI | گزینه‌های `--rule-pack` و `--sarif-output` | اجرای قواعد سازمانی و تولید SARIF در خط لوله |
| بسته‌بندی ویندوز | افزودن Rule Pack به داده‌های PyInstaller و اجرای آزمون‌ها در GitHub Actions | جلوگیری از حذف Rule Pack پیش‌فرض از EXE منتشرشده |

## مرزهای امنیت و حریم خصوصی

| موضوع | رفتار v1.0.4 | مسئولیت Release Owner |
|---|---|---|
| Rule Pack | فقط JSON خوانده می‌شود؛ اجرای کد، `eval`، Plugin و subprocess پشتیبانی نمی‌شود. | Rule Pack سازمانی را در کنترل نسخه، بازبینی و آزمایش نگه دارد. |
| Regex نامعتبر | Rule نامعتبر Notice ایجاد می‌کند و اسکن را متوقف نمی‌کند. | Noticeها را پیش از اتکا به نتیجه اسکن بررسی کند. |
| Trend History | فقط timestamp، هش مسیر، شمارش یافته، شدت، دسته، Rule ID و fingerprint هش‌شده ذخیره می‌شود. | محل فایل SQLite و سیاست نگهداشت/پاکسازی آن را با سیاست داده سازمان هماهنگ کند. |
| Cache Review | خروجی Review طبق رفتار Cache موجود ذخیره می‌شود. | محل Cache، دسترسی فایل و دوره نگهداشت را بازبینی کند. |
| SARIF | فایل محلی شامل metadata و متن یافته است و ممکن است در ابزار مقصد حساس تلقی شود. | پیش از Archive یا Upload، طبقه‌بندی داده و دسترسی Artifact را کنترل کند. |
| AI findings | یافته‌های AI یا Regex قطعی نیستند. | بازبینی انسانی و تست تغییر پیشنهادی پیش از اعمال لازم است. |

## تغییرات ناسازگار یا عملیاتی

نسخه v1.0.4 تغییر ناسازگار در API عمومی فعلی معرفی نمی‌کند. با این حال، کلید Cache Review اکنون نسخه تحلیل، مسیر فایل و امضای Rule Pack را در بر می‌گیرد تا تغییر Rule Pack نتیجه Cache قدیمی را بازنگرداند. اجرای CLI باید در محیطی باشد که وابستگی‌های `requirements.txt` نصب شده‌اند و مسیر Rule Pack در دسترس است.

## کنترل‌های پذیرش اجراشده

| کنترل | نتیجه | روش |
|---|---|---|
| Syntax check | موفق | `python -m py_compile core/ai_engine.py ui/main_window.py app.py` |
| اعتبارسنجی Rule Pack | موفق | `python -m json.tool rules/enterprise_default_rules.json` |
| آزمون Rule Pack چندزبانه | موفق | `unittest` برای Python، Java، Go و Rust |
| آزمون Rule Pack نامعتبر | موفق | تأیید ادامه Local SAST همراه با Notice |
| آزمون SARIF | موفق | تأیید `version=2.1.0`، Rule، location و fingerprint |
| آزمون حریم خصوصی Trend | موفق | تأیید عدم ذخیره متن کد در جدول تاریخچه |
| Smoke Test UI | موفق | ساخت UI با `QT_QPA_PLATFORM=offscreen` و بررسی صفحه/کنترل‌های جدید |
| کنترل Diff | موفق | `git diff --check` بدون خطای whitespace |

## چک‌لیست انتشار کنترل‌شده

| گام | مالک | وضعیت پیش از انتشار |
|---|---|---|
| مرور تغییرات و Rule Pack پیش‌فرض | Engineering Lead + Security | لازم |
| اجرای CI ویندوز و Unit Test | Release Owner | لازم |
| بررسی وجود Rule Pack در EXE | Release Owner | لازم |
| اجرای Smoke Test دستی روی ویندوز | QA | لازم |
| تولید SARIF نمونه و بررسی با JSON Parser | QA/Security | لازم |
| بررسی مجوز Code Scanning پیش از Upload SARIF | GitHub Admin | در صورت فعال‌سازی Integration |
| تدوین Release Notes در GitHub | Release Owner | لازم |
| انتشار tag `v1.0.4` | Release Owner | پس از تکمیل موارد بالا |
| بررسی Asset و Checksum دانلود | Release Owner | پس از انتشار |

## Rollback

در صورت مشاهده خطای راه‌اندازی، Rule Pack خارج از انتظار یا Regression در مسیر Review، Release Owner باید انتشار را متوقف کند، tag را به‌عنوان نامناسب علامت‌گذاری کند و نسخه پایدار قبلی را به مشتریان هدایت کند. Cache محلی را می‌توان با حذف فایل `review_cache.db` بازسازی کرد؛ پیش از حذف، مالک دستگاه باید آثار نگهداشت داده را بررسی کند. Rollback نباید به حذف شواهد Incident یا فایل‌های موردنیاز بررسی امنیتی منجر شود.

## منابع

[1]: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html "OASIS — Static Analysis Results Interchange Format (SARIF) Version 2.1.0"
[2]: https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file "GitHub Docs — Uploading a SARIF file to GitHub"

> انتشار این نسخه به معنی گواهی انطباق، تضمین نبود آسیب‌پذیری یا جایگزینی آزمایش امنیتی مستقل نیست. هر استقرار Enterprise باید با مدل تهدید، سیاست داده و کنترل‌های مشتری نهایی هم‌راستا شود.
