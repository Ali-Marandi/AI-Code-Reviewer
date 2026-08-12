# پیگیری انتشار v1.0.6

| مورد | وضعیت |
|---|---|
| Commit | `58c2b73` — `test: close SQLite inspection connection on Windows` |
| Tag | `v1.0.6` |
| GitHub Actions Run | `Build Windows EXE #7` با Run ID `31647754079` |
| وضعیت نهایی | موفق؛ Build Windows EXE #7 در ۲ دقیقه و ۴۷ ثانیه تکمیل شد. |
| هدف وصله | رفع آخرین `WinError 32` در cleanup آزمون SQLite روی Windows |

## کنترل‌های محلی تکمیل‌شده

Syntax check، ۵ آزمون واحد Enterprise، Smoke Test رابط PySide6 در حالت Offscreen و بررسی `git diff --check` با موفقیت انجام شده‌اند.

## انتشار تأییدشده

GitHub Release `v1.0.6` به‌عنوان Latest منتشر شد و فایل `AI-Code-Reviewer-Enterprise.exe` با اندازه ۶۰٫۶ مگابایت در Assets آن موجود است. SHA-256 منتشرشده توسط GitHub: `c1d721f7c0fde3ae88d94ccc9304caab71020871816b3c09a9e28b9f29cf2996`.

## یادداشت CI

GitHub Actions در اجرای نهایی فقط هشدار deprecation مربوط به Node.js 20 برای `actions/checkout@v4`، `actions/setup-python@v5` و `softprops/action-gh-release@v2` نمایش داد و Job با موفقیت تکمیل شد. این هشدار مانع Build یا انتشار نشد، اما باید در چرخه نگهداشت CI بررسی شود.
