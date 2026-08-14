# راهنمای اجرایی ۳۰ روزه و شروع پایلوت سازمانی AI-Code-Reviewer

**نویسنده:** Manus AI  
**تاریخ:** ۱۴ اوت ۲۰۲۶  
**کاربرد:** تبدیل نسخهٔ فعلی محصول به یک بتای کنترل‌شده و اجرای نخستین پایلوت سازمانی، بدون ادعای آمادگی کامل Enterprise پیش از گذر از Gateهای امنیتی.

---

## خلاصهٔ عملیاتی

این برنامه برای یک تیم کوچک محصول طراحی شده است: یک Lead Engineer، یک Desktop Engineer، یک DevSecOps/Security Engineer، یک Product/Customer Lead و یک نفر QA که می‌تواند پاره‌وقت باشد. هدف ۳۰ روز نخست فروش وسیع یا انتشار عمومی نیست؛ هدف، **اثبات یک جریان امن و قابل‌اندازه‌گیری** با سه design partner واجد شرایط است.

> **قاعدهٔ توقف:** تا وقتی credential storage، license integrity، consent telemetry و release signing به Gate پذیرش نرسیده‌اند، هیچ کد مشتری برای تحلیل AI خارج از boundary تأییدشدهٔ او ارسال نمی‌شود و هیچ feature Enterprise فروخته یا فعال نمی‌شود.

---

## ۱. پیش‌نیازهای روز صفر

پیش از شروع تقویم، مدیر محصول باید مالک هر نتیجه را تعیین کند و یک workspace واحد برای issueها، تصمیم‌ها، risk register و شواهد ایجاد کند. هیچ فعالیتی نباید با توکن شخصی دارای دسترسی وسیع یا یک trial license ساختگی انجام شود.

| مورد | مالک | خروجی قابل‌پذیرش |
|---|---|---|
| Rotate credentials | Repository Owner | PAT قبلی لغو شده، توکن جدید fine-grained یا GitHub App با حداقل scope ساخته شده است |
| Freeze scope | Product Lead | تصمیم روشن: در این ۳۰ روز تنها GitHub + Windows + local/SAST/approved AI gateway پشتیبانی می‌شود |
| Branch protection | Engineering Lead | PR review اجباری، status check اجباری و عدم push مستقیم به `main` |
| Risk register | Security Lead | ریسک credential، egress، license، telemetry، release و support ثبت شده است |
| Pilot scorecard | Product Lead | baseline، KPI، audience و exit criteria برای هر design partner آماده است |
| Support channel | Customer Lead | کانال امن برای هر مشتری، زمان پاسخ و مسیر escalation تعریف شده است |

---

## ۲. نقش‌ها و نظام تصمیم‌گیری

| نقش | مسئولیت اصلی | اختیار تصمیم |
|---|---|---|
| Product Lead | انتخاب customer، تعریف outcome، قیمت/offer، هماهنگی پایلوت | توقف یا تمدید پایلوت؛ تغییر KPI با ثبت دلیل |
| Engineering Lead | معماری، roadmap، review کد و quality gate | رد merge ناامن؛ اولویت‌بندی defectها |
| Desktop Engineer | PySide6، SecretStore، Windows packaging، UI consent | اجرا و test روی Windows clean VM |
| Security / DevSecOps | threat model، secrets، signing، DPA/data flow، release approval | block کردن release یا egress کنترل‌نشده |
| QA Engineer | test plan، regression، smoke test installer | sign-off کیفی برای pilot build |
| Customer Champion | هماهنگی تیم مشتری، جمع‌آوری feedback و escalation | تأیید معیار موفقیت عملیاتی از سمت مشتری |
| Executive Sponsor مشتری | تصمیم تجاری و رفع موانع سازمانی | go/no-go برای تمدید/خرید |

جلسهٔ داخلی روزانه ۱۵ دقیقه و جلسهٔ هفتگی تصمیم ۳۰ دقیقه کافی است. هر تغییر در policy، schema telemetry، provider AI، price یا entitlement باید یک decision record کوتاه با owner، تاریخ و اثر امنیتی داشته باشد.

---

## ۳. برنامهٔ گام‌به‌گام ۳۰ روزه

### هفتهٔ اول — رفع خطرهای P0 و طراحی contractها

| روز | اقدام دقیق | مالک | شواهد پایان روز |
|---:|---|---|---|
| ۱ | Rotate همهٔ tokenهای در معرض دید، پاک‌سازی remote URLها، اجرای secret scan روی history و source. | Security + Repo Owner | فهرست tokenهای لغوشده و scan report؛ هیچ secret فعال در repo نیست |
| ۲ | Threat-model workshop: رسم data flow برای token، code diff، AI provider، telemetry و license. | Security + Engineering | نسخهٔ اول data-flow، ۱۰ threat برتر و mitigation owner |
| ۳ | تعریف interface `SecretStore` و انتخاب Windows credential adapter؛ تعیین contract برای Sign out / uninstall / recovery. | Desktop + Engineering | ADR منتشرشده و test matrix Windows آماده |
| ۴ | طراحی entitlement schema و key-management procedure؛ ایجاد key ring عمومی و محیط issuance جداگانه. | Platform + Security | schema review شده؛ private key خارج از repo و خارج از client |
| ۵ | تعریف telemetry allowlist، consent copy و retention/deletion behavior؛ default telemetry را Disabled کنید. | Product + Security | event schema، UX copy و test cases approval شده |
| ۶ | طراحی pipeline release: secret scan، tests، SBOM، packaging، code signing، hash verification. | DevSecOps | workflow diagram و checklist signing با owner |
| ۷ | Review Gate W1: فقط اگر P0 plan، risk register و architecture decisionها تأیید شده‌اند وارد implementation شوید. | همهٔ leadها | صورت‌جلسهٔ gate: Go / Hold با دلیل |

### هفتهٔ دوم — پیاده‌سازی و آزمون کنترل‌های اصلی

| روز | اقدام دقیق | مالک | شواهد پایان روز |
|---:|---|---|---|
| ۸ | پیاده‌سازی `SecretStore` و adapter Windows؛ حذف هر persistence مبتنی بر JSON/QSettings برای secrets. | Desktop | unit test create/read/delete و failure handling |
| ۹ | اتصال Settings UI به «Save on this device»؛ Sign out را به delete credential وصل کنید. | Desktop + QA | تست دستی clean Windows user و screenshot test |
| ۱۰ | deprecate کردن `--token` و افزودن environment/secret-manager mode برای CLI. | Engineering | CLI test ثابت می‌کند token در argv/log چاپ نمی‌شود |
| ۱۱ | پیاده‌سازی signed entitlement verification و feature gates؛ حذف prefix-based `LicenseManager`. | Platform | tests برای tampered/expired/wrong-audience license |
| ۱۲ | پیاده‌سازی key rotation (`kid`) و رفتار offline grace؛ طراحی admin renewal path. | Platform + Security | testهای key ring و expiry/grace پاس می‌شوند |
| ۱۳ | جایگزینی telemetry file با queue schema-validated و consent UI؛ دکمهٔ disable/export/delete اضافه شود. | Desktop + Security | test نشان می‌دهد بدون consent هیچ analytics event ساخته نمی‌شود |
| ۱۴ | central logging + secret redactor + crash-report scrubber. | DevSecOps | test suite شامل token/header/path redaction |

### هفتهٔ سوم — کیفیت انتشار و آماده‌سازی پایلوت

| روز | اقدام دقیق | مالک | شواهد پایان روز |
|---:|---|---|---|
| ۱۵ | اضافه‌کردن test suite برای rule pack، SARIF، SecretStore، license و telemetry. | QA + Engineering | coverage report و test failures triaged |
| ۱۶ | ساخت clean Windows VM matrix: Windows 10/11، standard user، offline mode و corporate proxy. | QA | compatibility report و defect list |
| ۱۷ | ایجاد SBOM، dependency review و release manifest؛ بررسی اینکه هیچ development secret در artifact نیست. | DevSecOps | SBOM و scan report attached to build |
| ۱۸ | بسته‌بندی و امضای installer/EXE در staging؛ verify با `signtool` یا equivalent. | DevSecOps | signed artifact، hash و verification log |
| ۱۹ | انتشار AI System Card، data-flow، SECURITY.md، pilot data-handling note و known limitations. | Security + Product | docs در repository و approval Security |
| ۲۰ | Freeze pilot candidate؛ فقط defectهای P0/P1 و feedback blocker پذیرفته می‌شوند. | Engineering Lead | release candidate tag و changelog |
| ۲۱ | Review Gate W3: Quality, security و product sign-off؛ در صورت fail، پایلوت آغاز نمی‌شود. | Leads + Sponsor | signed go/no-go record |

### هفتهٔ چهارم — اجرا و اندازه‌گیری پایلوت

| روز | اقدام دقیق | مالک | شواهد پایان روز |
|---:|---|---|---|
| ۲۲ | انتخاب سه design partner و امضای pilot charter؛ scope هر مشتری حداکثر ۱–۳ repository و ۱۰–۲۵ seat فعال. | Product + Customer | charter امضاشده و champions مشخص |
| ۲۳ | Security onboarding مشتری: deployment boundary، GitHub App permission، data egress و support contact. | Security + Customer | customer security checklist completed |
| ۲۴ | نصب guided، اتصال GitHub، بارگذاری rule pack و اولین review در حضور champion. | Desktop + Customer | time-to-first-review و install log scrubbed |
| ۲۵ | ثبت baseline: PR throughput، median review time، تعداد findingهای بحرانی و current toolchain. | Product | baseline worksheet برای هر pilot |
| ۲۶ | فعال‌سازی review فقط برای PRهای non-draft و pathهای کم‌ریسک؛ human review اجباری باقی می‌ماند. | Customer Champion | policy/config snapshot و first-week coverage |
| ۲۷ | جلسهٔ feedback ۳۰ دقیقه‌ای با authors/reviewers؛ triage false positives و missing context. | Product + Engineering | structured feedback with finding IDs |
| ۲۸ | اعمال فقط fixes کم‌خطر و versioned rule-pack update؛ هیچ change از feedback مستقیم در production بدون review نمی‌رود. | Engineering + Security | changelog، regression test و rollback plan |
| ۲۹ | بررسی KPI و customer sentiment؛ تحلیل هزینهٔ RU/AI و budget behavior. | Product + Finance/Operations | scorecard draft و risk items |
| ۳۰ | Executive readout: evidence، limitationها، roadmap، commercial proposal و decision gate. | Product + Sponsor | Go / Extend / Stop decision با owner و تاریخ |

---

## ۴. انتخاب Design Partner مناسب

پایلوت از نظر تجاری موفق نیست اگر فقط با کاربرانی اجرا شود که product را دوست دارند اما اختیار یا بودجهٔ خرید ندارند. شریک طراحی ایده‌آل هم «درد واقعی» دارد و هم توان تبدیل به قرارداد.

| معیار | نشانهٔ مناسب | نشانهٔ نامناسب |
|---|---|---|
| جریان کاری | GitHub-centric، PR-based و حداقل ۲۰ PR در هفته در scope پایلوت | فرآیند بدون PR یا migration بزرگ و ناپایدار |
| نیاز امنیتی | AI coding adoption همراه با نیاز policy/compliance یا محدودیت data egress | انتظار ابزار کاملاً خودکار برای approve/merge |
| توان خرید | Sponsor با budget authority و procurement path مشخص | فقط یک developer کنجکاو بدون champion یا budget |
| آمادگی فنی | می‌تواند GitHub App یا least-privilege token و test repo فراهم کند | نیاز به دسترسی admin گسترده یا production secrets در هفتهٔ اول |
| همکاری | feedback هفتگی و امکان share کردن KPI تجمیعی | دسترسی نامنظم و عدم willingness برای measurement |

پیشنهاد می‌شود هر design partner با یک **Pilot Charter** یک‌صفحه‌ای شروع کند که هدف، repositoryهای در scope، تعداد seat، data boundary، integrations، KPI، زمان‌بندی، نقش‌ها، support window و شرط توقف را به‌صورت روشن ثبت کند. این charter جایگزین DPA، NDA یا قرارداد اصلی نیست؛ اسناد حقوقی و privacy باید توسط مشاور حقوقی و تیم procurement بررسی شوند.

---

## ۵. Onboarding سازمانی قدم‌به‌قدم

### گام ۱: جلسهٔ Discovery و توافق بر مسئله

در جلسهٔ ۴۵ دقیقه‌ای از sponsor و champion بخواهید یک pain قابل‌اندازه‌گیری انتخاب کنند: کاهش زمان review PRهای کم‌ریسک، کنترل policy برای AI-generated code، یا ایجاد evidence برای audit. از عبارت‌های مبهم مانند «می‌خواهیم AI بهتر شود» استفاده نشود. مشتری باید baseline مربوط به همان outcome را قبل از نصب تأیید کند.

### گام ۲: Data and Security Review

نقشهٔ مسیر داده را با مشتری مرور کنید. روشن کنید که چه چیزی local می‌ماند، چه زمانی diff به مدل خارجی می‌رود، آیا مدل BYO/customer-hosted است، telemetry چه داده‌ای ندارد و چگونه می‌توان آن را حذف کرد. تا زمانی که approval لازم برای provider AI دریافت نشده است، برنامه تنها local SAST و rule packs را اجرا می‌کند.

### گام ۳: Access با حداقل مجوز

GitHub App با scope حداقلی و installation فقط روی repositoryهای پایلوت ترجیح دارد. اگر PAT ضروری است، fine-grained، repository-scoped، کوتاه‌عمر و در OS store نگهداری می‌شود. هرگز token مشترک تیمی، توکن Administrator یا credentialی که در spreadsheet ارسال شده است استفاده نشود.

### گام ۴: نصب، لایسنس و First Value

Installer امضاشده را با hash منتشرشده دریافت و verify کنید. entitlement trial امضاشده را import کنید، نه یک string دستی. سپس یک PR غیرحساس و non-draft انتخاب کنید؛ rule pack پیش‌فرض را اجرا کنید و اولین finding قابل‌توضیح را با reviewer بررسی کنید. هدف روز اول یک review کامل و صحیح است، نه حداکثر coverage.

### گام ۵: Policy Calibration

در هفتهٔ اول، pathهای generated، vendor، lockfile، test fixture و deployment manifest از auto-review مستثنی شوند مگر اینکه هدف پایلوت دقیقاً آن‌ها باشد. Severity rubric با مشتری هماهنگ شود. هر suppression باید reason، author، date و expiry داشته باشد. اگر findingهای AI noise تولید می‌کنند، confidence threshold یا review depth تغییر می‌کند؛ کیفیت قبل از coverage است.

### گام ۶: Cadence، Feedback و Fix

هر هفته یک جلسهٔ ۳۰ دقیقه‌ای برگزار می‌شود. فقط feedback دارای finding ID، severity، action و علت dismissal برای بهبود rule/AI در backlog قرار می‌گیرد. هر تغییر policy versioned و test می‌شود؛ deployment بدون rollback یا regression test ممنوع است.

---

## ۶. KPI، Baseline و معیار موفقیت

KPI باید با منبع داده و تعریف ثابت ثبت شوند. «تعداد comment» معیار موفقیت نیست؛ ممکن است فقط noise را اندازه بگیرد.

| KPI | تعریف | نحوهٔ baseline | هدف پیشنهادی برای پایلوت |
|---|---|---|---|
| Time to First Value | زمان از نصب تا نخستین review کامل | timestamp install و review result | کمتر از ۳۰ دقیقه با onboarding guided |
| Eligible PR Coverage | PRهای واجد شرایط بررسی‌شده / همهٔ PRهای واجد شرایط | GitHub PR count + review run count | حداقل ۵۰٪ تا پایان هفتهٔ دوم پایلوت |
| Finding Action Rate | findingهای Accepted/Fixed/Useful / findingهای دارای disposition | disposition در UI یا feedback form | حداقل ۴۰٪؛ در غیر این صورت signal quality بازبینی می‌شود |
| False Positive Rate | findingهای Dismissed as incorrect / findingهای دارای disposition | feedback reason codes | روند کاهشی هفته‌به‌هفته؛ target نهایی پس از baseline تعیین می‌شود |
| Reviewer Time | median زمان تا تصمیم reviewer برای PRهای scope | دادهٔ مشتری یا sample دستی | بهبود فقط در مقایسه با baseline مشتری اعلام می‌شود |
| Security Value | findingهای high/critical تأییدشده | triage مشترک، نه ادعای خودکار | حداقل یک finding معتبر یا مستند کردن «عدم وجود یافته» |
| Customer Sentiment | NPS-like qualitative + willingness to pay | مصاحبهٔ sponsor/champion | sponsor حاضر به مذاکرهٔ قرارداد یا extension باشد |

اهداف فوق **فرضیهٔ پایلوت** هستند، نه benchmark بازار. اگر مشتری baseline ندارد، سه تا پنج روز اول صرف ثبت baseline می‌شود و هیچ ادعای ROI کمی مطرح نمی‌گردد.

---

## ۷. Pilot Governance و مسیر Escalation

| رخداد | زمان پاسخ هدف | مالک نخست | مسیر بعدی |
|---|---:|---|---|
| نشت یا احتمال نشت credential/data | فوری؛ حداکثر ۱ ساعت برای acknowledgement | Security Lead | توقف egress، rotation، incident lead، اطلاع‌رسانی طبق قرارداد |
| false positive High/Critical | ۱ روز کاری | Engineering Lead | triage، rule rollback یا suppression موقت versioned |
| crash installer یا عدم اجرای برنامه | ۱ روز کاری | Desktop Engineer | QA reproduction، hotfix release در صورت blocker |
| اختلاف license/entitlement | ۱ روز کاری | Customer Lead + Platform | audit entitlement و issue signed replacement |
| درخواست feature | جلسهٔ هفتگی | Product Lead | backlog با impact و status واضح |

هر incident باید evidence و timeline داشته باشد، اما telemetry/logهای منتقل‌شده به تیم محصول باید scrub شوند. برای incident واقعی، privacy/security contact مشتری و الزامات قراردادی او بر روند داخلی اولویت دارد.

---

## ۸. تصمیم روز ۳۰: Go، Extend یا Stop

| تصمیم | شرایط | اقدام بعدی |
|---|---|---|
| Go to paid conversion | Gateهای امنیتی برقرار، champion/sponsor value را تأیید می‌کنند، حداقل یک outcome قابل‌اندازه‌گیری وجود دارد | proposal سالانه، entitlement production، security/procurement plan و rollout تدریجی |
| Extend pilot | security قابل‌قبول است اما baseline/KPI ناکافی یا deployment محدود بوده است | تمدید ۳۰ روزه با یک hypothesis و success criterion جدید؛ بدون scope creep |
| Stop | data boundary قابل تأیید نیست، false-positive شدید است، customer engagement کافی نیست یا P0 security failure رخ داده است | uninstall/credential deletion، data deletion confirmation، retrospective و توقف فروش به account |

---

## ۹. خروجی‌های الزامی پایان ۳۰ روز

| خروجی | مخاطب | وضعیت لازم |
|---|---|---|
| Threat model و data-flow versioned | Security/customer | تأیید شده |
| AI System Card و known limitations | Customer/reviewer | منتشر و قابل‌دسترسی |
| Signed release evidence: hash, signature, SBOM | IT/security مشتری | قابل‌verify |
| Entitlement record و license audit trail | Operations/procurement | کامل و بدون secret |
| Pilot scorecard و baseline | Sponsor | شامل نتیجه، limitation و ROI evidence |
| Security incident / support log scrubbed | تیم داخلی | کامل یا صراحتاً “none” |
| Commercial proposal یا stop memo | Sponsor + Product | تاریخ decision بعدی مشخص |

---

## افشا و حدود راهنما

**مبنا:** برنامه از معماری و ممیزی static کد فعلی محصول مشتق شده است.  
**زمان:** روز ۱ تا روز ۳۰ از زمانی آغاز می‌شود که پیش‌نیازهای روز صفر تکمیل شده باشند.  
**فرض‌ها:** تیم پنج‌نفرهٔ هسته‌ای، سه design partner و scope محدود GitHub/Windows وجود دارد.  
**منابع و اطمینان:** کنترل‌های پایه به مستندات رسمی Windows/NIST در سند طراحی امنیت و لایسنسینگ پیوست ارجاع داده شده‌اند؛ KPIها و زمان‌بندی توصیه‌های اجرایی‌اند و باید با ظرفیت تیم و قرارداد مشتری تنظیم شوند.  
**انطباق:** این راهنما مشاورهٔ حقوقی، تعهد SLA یا گواهی compliance نیست.

---
**Prepared by Manus AI**
