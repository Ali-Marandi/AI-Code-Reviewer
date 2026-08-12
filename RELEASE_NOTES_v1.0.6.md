# یادداشت انتشار — v1.0.6

**AI-Code-Reviewer Enterprise**
**نوع انتشار:** Patch Release برای تکمیل سازگاری آزمون روی Windows
**وضعیت:** آماده انتشار کنترل‌شده

## تغییر

v1.0.6 آخرین اتصال SQLite بازمانده در خود آزمون حریم خصوصی تاریخچه را به‌صورت صریح می‌بندد. این تغییر مکمل v1.0.5 است که چرخه اتصال SQLite در هسته را به `commit/rollback/close` قطعی تغییر داد.

| مورد | نتیجه |
|---|---|
| هسته SQLite | اتصال‌های Cache و History پس از هر عملیات بسته می‌شوند. |
| آزمون حریم خصوصی History | اتصال بازرسی مستقیم SQLite در تست با `finally: connection.close()` بسته می‌شود. |
| CI Windows | خطای `WinError 32` ناشی از فایل موقت قفل‌شده نباید دیگر در `TemporaryDirectory.cleanup()` رخ دهد. |
| قابلیت‌های Enterprise | Rule Pack، SARIF Export و Findings Trend بدون تغییر باقی مانده‌اند. |

## کنترل‌های قبل از انتشار

| کنترل | نتیجه |
|---|---|
| Syntax check هسته، UI و CLI | موفق |
| Unit testهای Enterprise | ۵ از ۵ موفق |
| Smoke Test PySide6 در حالت Offscreen | موفق |
| کنترل whitespace در Diff | موفق |

> این Patch هیچ خروجی داده جدیدی به سرویس بیرونی ارسال نمی‌کند و تنها پایداری Lifecycle اتصال SQLite را در هسته و آزمون‌ها تکمیل می‌کند.
