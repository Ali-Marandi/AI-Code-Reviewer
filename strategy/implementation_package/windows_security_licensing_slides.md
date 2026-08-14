## Cover

# AI-Code-Reviewer Enterprise
## معماری امنیت ویندوز و مدل لایسنسینگ قابل‌اعتماد
### تصمیم‌های اجرایی برای پایلوت سازمانی — ۱۴ اوت ۲۰۲۶

## Slide 1

# اعتماد، محصول است؛ نه یک قابلیت جانبی

- مسیر فعلی local-first پایهٔ درستی دارد، اما secret storage، license validation و telemetry هنوز prototype-grade هستند.
- مسیر موفق Enterprise: **حداقل‌سازی داده + کنترل OS + entitlement امضاشده + انتشار قابل‌اثبات**.
- اصل عملیاتی: هیچ کد یا credentialی بدون نیاز، رضایت و boundary روشن جابه‌جا یا ذخیره نمی‌شود.

## Slide 2

# ریسک فوری: Token افشاشده و Release با سطح دسترسی گسترده

- PAT افشاشده باید compromised تلقی شود: **اکنون revoke؛ سپس جایگزینی با credential حداقل‌مجوز**.
- workflow فعلی publish را با `contents: write`، action tagهای mutable و dependencyهای بدون lock در یک job پیوند می‌زند.
- توقف کوتاه release بهتر از انتشار artifact امضانشده یا credential تکرارپذیر است.

## Slide 3

# معماری هدف: چهار boundary، یک زنجیرهٔ اعتماد

- **Identity:** GitHub App/OAuth و OS Credential Store؛ token شخصیِ بلندمدت مسیر پیش‌فرض نیست.
- **Analysis:** SAST و policy محلی؛ AI فقط از gateway تأییدشده و قابل‌کنترل عبور می‌کند.
- **Entitlement:** license امضاشده، کلید عمومی داخل client و کلید خصوصی خارج از client.
- **Release:** build ایزوله → sign → verify → publish با approval محافظت‌شده.

## Slide 4

# Windows Keychain: secret کوچک در OS، تنظیمات حساس در DPAPI

- GitHub/OAuth refresh token و کلید AI اختیاری فقط در Credential Manager/Credential Locker نگهداری می‌شوند.
- تنظیمات حساس کوچک با DPAPI در محدودهٔ **CurrentUser** رمز می‌شوند؛ `LOCAL_MACHINE` برای token کاربر ممنوع است.
- source code، diff، token و API key هرگز در QSettings، JSON، SQLite یا log ثبت نمی‌شوند.
- Sign out، credential را فوراً حذف می‌کند؛ CLI از environment/secret manager کوتاه‌عمر استفاده می‌کند.

## Slide 5

# جریان بررسی: local-first با egress کنترل‌شده

- PR/فایل → rule pack و SAST محلی → context محدود → AI Gateway تأییدشده، فقط در صورت مجازبودن.
- هر finding منشأ خود را اعلام می‌کند: deterministic، custom policy یا AI-assisted.
- history محلی فقط hash و metadata ضروری دارد؛ telemetry به کد، URL، نام مخزن یا exception raw دسترسی ندارد.
- انسان تصمیم نهایی است: پیشنهاد AI می‌تواند patch بسازد، اما merge خودکار ندارد.

## Slide 6

# لایسنس Enterprise: جعل‌پذیر نیست، قابل‌مدیریت است

- پیشوندی مانند `AI-ENT-*` هیچ امنیتی ایجاد نمی‌کند؛ باید حذف شود.
- entitlement شامل tenant، SKU، feature، seat limit، RU، expiry، grace و `kid` است.
- EdDSA/Ed25519 یا ECDSA P-256 با کتابخانهٔ cryptography review‌شده؛ private key فقط در issuance service.
- key rotation، signed revocation و entitlement renewal، دفاع لایه‌ای در برابر misuse فراهم می‌کنند.

## Slide 7

# بسته‌بندی تجاری: پیش‌بینی‌پذیری برای مشتری، کنترل هزینه برای ما

| Tier | Commercial logic | Entitlement highlight |
|---|---|---|
| Community | Local-first adoption | SAST، SARIF، RU آزمایشی محدود |
| Team | US$25 / seat / month annual | GitHub integration، custom rules، RU pooled |
| Business | US$39 / seat / month annual | GitHub App، policy controls، dashboards |
| Enterprise Cloud | US$55 / seat / month annual | SSO/SCIM، RBAC، audit، SLA، data residency |
| Enterprise Self-Hosted | Platform fee + US$35 / seat / month | VPC/on-prem، BYO gateway، offline entitlement |

**مدل مصرف:** deterministic analysis رایگان؛ AI Review Unit شفاف، pooled و budget-capped.

## Slide 8

# Telemetry: رضایت واقعی، نه یک toggle مبهم

- دو جریان مستقل: **service/security essential** و **optional product analytics**.
- Analytics اختیاری به‌صورت پیش‌فرض خاموش است؛ «ادامه بدون analytics» هم‌ارز و بدون افت قابلیت local است.
- consent receipt حداقلی: purpose، decision، policy version، timestamp و source؛ نه کد یا شناسهٔ پروژه.
- Withdrawal فوری: upload متوقف، صف اختیاری حذف و UI وضعیت policy سازمان را شفاف نشان می‌دهد.

## Slide 9

# CI/CD: Build هرگز حق انتشار ندارد

- **Validate:** read-only، test، lint، secret scan و dependency audit.
- **Build:** read-only، dependency lock/hash، SBOM و checksum؛ هیچ publish secret ندارد.
- **Sign:** protected environment، approval و managed signing/HSM.
- **Publish:** تنها job دارای `contents: write`؛ actionها با full commit SHA pin و artifact قبل از upload verify می‌شود.

## Slide 10

# ۳۰ روز تا پایلوت کنترل‌شده

| بازه | خروجی غیرقابل‌مذاکره |
|---|---|
| روزهای ۱–۷ | revoke/inventory، threat model، SecretStore و entitlement schema |
| روزهای ۸–۱۴ | Windows credential adapter، license verify، telemetry consent و redaction tests |
| روزهای ۱۵–۲۱ | signed release candidate، SBOM، AI System Card و security gate |
| روزهای ۲۲–۳۰ | سه design partner، onboarding محدود، baseline/KPI و تصمیم Go/Extend/Stop |

**قاعدهٔ Gate:** بدون storage امن، consent واقعی و artifact امضانشده، پایلوت شروع نمی‌شود.

## Slide 11

# تصمیم امروز: سه اقدام، یک مالک، یک Deadline

- **Security Lead:** PAT را revoke و inventory credential را ظرف ۶۰ دقیقه تکمیل کند.
- **Engineering Lead:** workflow انتشار را به Validate → Build → Sign → Publish تفکیک و SHA pinning را اجباری کند.
- **Product/Privacy Lead:** telemetry optional را default-off و policy-managed کند؛ سپس سه design partner واجد شرایط را انتخاب کند.

> هدف: نخستین قرارداد Enterprise را با «کنترل و اعتماد» ببریم، نه با وعدهٔ review خودکار.

## Slide 12

# منابع و محدودیت‌ها

- Microsoft Learn: DPAPI، Credential Locker و Code Signing Options
- NIST: FIPS 186-5 Digital Signature Standard
- GitHub Docs: Token Revocation و Secure Use of GitHub Actions
- EDPB Guidelines 05/2020 و ICO Consent Guidance

قیمت‌ها و ظرفیت Review Unit، فرضیه‌های اولیهٔ پایلوت هستند و پیش از quote عمومی باید با هزینهٔ مدل، procurement و counsel بازبینی شوند.
