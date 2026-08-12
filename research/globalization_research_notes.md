# یادداشت پژوهش جهانی‌سازی محصول

## منابع رسمی بررسی‌شده

| موضوع | منبع | یافته کاربردی |
|---|---|---|
| محلی‌سازی Qt | [Qt — Localizing Applications](https://doc.qt.io/qt-6/localization.html) | چرخه استاندارد شامل قابل‌ترجمه‌کردن رشته‌ها، استخراج با `lupdate`، ترجمه TS و تولید QM با `lrelease` است. فایل‌های QM باید همراه برنامه منتشر شوند؛ Qt هشدار می‌دهد ترجمه‌های ارسالی جامعه باید پیش از عرضه ممیزی شوند. |
| بارگذاری ترجمه PySide6 | [Qt for Python — QTranslator](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QTranslator.html) | Translator باید پیش از ایجاد Widgetها ساخته و نصب شود؛ فایل‌های ترجمه فقط از منابع مورداعتماد باید بارگذاری شوند. |
| ابزار مدیریت ترجمه | [PySide6 Linguist](https://doc.qt.io/qtforpython-6/tools/pyside-linguist.html) | ابزار Qt Linguist و قالب TS/XLIFF برای مدیریت Localisation در دسترس است. |
| حریم خصوصی اتحادیه اروپا | [European Commission — GDPR principles](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/principles-gdpr_en) | شفافیت، محدودیت هدف، کمینه‌سازی داده، محدودیت نگهداشت، دقت، محرمانگی و پاسخ‌گویی اصول مرکزی‌اند. Privacy-by-design/default و کنترل انتقال داده برون‌مرزی باید از ابتدا دیده شوند. |
| توسعه امن | [NIST SSDF](https://csrc.nist.gov/projects/ssdf) | چهار حوزه آماده‌سازی، حفاظت از نرم‌افزار، تولید امن و پاسخ به آسیب‌پذیری‌ها برای برنامه‌ریزی مبتنی بر ریسک مناسب‌اند. |
| معیار امنیتی | [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) | ASVS مبنای قابل استفاده برای آزمون کنترل‌های فنی، راهنمای توسعه و تعریف نیازمندی قراردادی ارزیابی امنیتی است؛ شناسه نسخه‌دار باید در کنترل‌ها ثبت شود. |

## نتیجه‌گیری اجرایی

برای عرضه جهانی AI-Code-Reviewer، ترتیب درست عملیات عبارت است از: تثبیت Release و زنجیره تأمین، محلی‌سازی قابل ممیزی با منابع ترجمه مورداعتماد، تعریف مدل پردازش داده و نگهداشت برای هر بازار، و سپس اجرای پایلوت محدود مبتنی بر معیارهای Exit. ادعای انطباق یا گواهی بدون ارزیابی حقوقی و امنیتی مستقل نباید در بازاریابی یا قراردادها مطرح شود.
