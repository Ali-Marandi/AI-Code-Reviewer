# یادداشت انتشار — v1.0.5

**AI-Code-Reviewer Enterprise**
**نوع انتشار:** Patch Release برای سازگاری CI ویندوز
**وضعیت:** آماده ساخت مجدد پس از آزمون محلی موفق

## مشکل رفع‌شده

Build v1.0.4 در GitHub Actions ویندوز، در مرحله اجرای آزمون‌های واحد متوقف شد. علت اصلی، بازماندن handle اتصال SQLite بعد از خروج از Context Manager بود. در ویندوز، این رفتار مانع حذف پایگاه داده موقت توسط `TemporaryDirectory` می‌شد و تمام آزمون‌ها را در مرحله `tearDown` با `WinError 32` ناموفق می‌کرد.

## وصله اعمال‌شده

| تغییر | اثر |
|---|---|
| Context Manager اختصاصی SQLite | اتصال را در همه مسیرها به‌صورت صریح `commit` یا `rollback` و سپس `close` می‌کند. |
| مسیرهای Cache و History | تمام عملیات Cache، ثبت History و Queryهای Trend از Context Manager بسته‌شونده استفاده می‌کنند. |
| نسخه رابط کاربری | عنوان پنجره و Sidebar به `v1.0.5` به‌روزرسانی شد. |

## کنترل‌های اجراشده پیش از انتشار

| کنترل | نتیجه |
|---|---|
| Syntax check هسته، UI و CLI | موفق |
| Unit testهای Rule Pack، SARIF و History | ۵ از ۵ موفق |
| Smoke Test رابط PySide6 در حالت Offscreen | موفق |
| کنترل whitespace در Diff | موفق |

> v1.0.5 جایگزین قابلیت‌های v1.0.4 نیست؛ همان قابلیت‌های Rule Pack، SARIF و Findings Trend را با اصلاح سازگاری SQLite در CI ویندوز منتشر می‌کند.
