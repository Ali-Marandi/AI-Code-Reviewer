# راهنمای اجرای فوری: ابطال GitHub Token و سخت‌سازی CI/CD

**نویسنده:** Manus AI  
**تاریخ:** ۱۴ اوت ۲۰۲۶  
**وضعیت:** دستورالعمل عملیاتی. این راهنما جایگزین response plan رسمی، بررسی forensic یا مشاورهٔ امنیتی تخصصی نیست.

---

## نتیجهٔ فوری

توکن GitHub که خارج از boundary محرمانه قرار گرفته است باید **هم‌اکنون compromised فرض شود**. حذف آن از remote URL، source code یا history امنیت credential را بازنمی‌گرداند. GitHub بیان می‌کند که token ابطال‌شده دیگر برای Git/API قابل‌استفاده نیست و قابل restore نیست؛ بنابراین راه درست، revoke و صدور credential جدید است. [1]

> **ترتیب درست:** revoke → inventory/replacement → verification → investigation → purge. هرگز برای پاک‌کردن history، revoke را به تأخیر نیندازید.

---

## ۱. Runbook ابطال و جایگزینی token

### در ۶۰ دقیقهٔ نخست

| گام | اقدام دقیق | مالک | مدرک انجام |
|---:|---|---|---|
| ۱ | در GitHub به **Settings → Developer settings → Personal access tokens** بروید و PAT افشاشده را Revoke کنید. اگر توکن classic است، classic token را لغو کنید؛ اگر fine-grained است، fine-grained token را لغو کنید. | Token owner | timestamp، نام token و نتیجهٔ revoke در incident record؛ مقدار token هرگز ثبت نشود |
| ۲ | هر session محلی که ممکن است token را cache کرده باشد، از جمله `gh auth`, Windows Credential Manager، keyring، shell environment و credential helper را logout/delete کنید. | Token owner + Desktop | inventory دارای status `removed` یا `not present` |
| ۳ | تا پایان hardening، publish/release automation را متوقف کنید: tag push و release job را فقط از طریق maintainer و protected environment مجاز کنید. | Repo admin | release freeze در incident record |
| ۴ | در GitHub Security Log و—برای سازمان—Audit Log، فعالیت‌های غیرمعمول از زمان نخستین exposure را بررسی کنید: token creation/revocation، repository access، SSH/GPG keys، app authorization، workflow و release events. | Security lead | review period و findings ثبت‌شده |
| ۵ | scope exposure را ثبت کنید: chat، terminal history، remote URL، CI logs، screenshots، release artifacts و هر local credential store. | Security lead | exposure inventory بدون درج secret |

### در ۲۴ ساعت نخست

| گام | اقدام دقیق | مالک | معیار اتمام |
|---:|---|---|---|
| ۶ | جست‌وجوی secret scanning را روی repository و history اجرا کنید؛ در صورت وجود secret فعال، آن را مستقل rotate کنید. | DevSecOps | report scrubbed و ticket برای هر finding |
| ۷ | بررسی کنید که remoteهای Git بدون token باشند: `https://github.com/OWNER/REPO.git` یا SSH، نه URL دارای credential. | Repo admin | `git remote -v` روی دستگاه‌های کاری امن است |
| ۸ | وابستگی‌های publish را از PAT انسانی جدا کنید. برای release داخلی، `GITHUB_TOKEN` کم‌مجوز در job protected؛ برای APIهای بیرونی، GitHub App installation token یا OIDC. | DevSecOps | معماری credential approved |
| ۹ | اگر history عمومی یا forkها token را دربرداشته‌اند، پس از revoke برای rewrite history و درخواست cache removal برنامه‌ریزی کنید. Rewriting history به تنهایی کافی نیست و می‌تواند developer workflow را مختل کند. | Repo admin | decision record و communication plan |
| ۱۰ | یک fine-grained PAT دارای expiry کوتاه فقط برای کار موقت بسازید، یا ترجیحاً GitHub App را جایگزین کنید. هیچ token جدیدی در chat، terminal command یا remote URL قرار نگیرد. | Token owner | scope/expiry/owner در asset inventory ثبت شده |

### در ۷ روز نخست

| گام | اقدام دقیق | مالک | معیار اتمام |
|---:|---|---|---|
| ۱۱ | GitHub App برای integration برنامه ایجاد کنید: repository installation محدود، permission حداقلی و tokenهای کوتاه‌عمر. | Platform | architecture review + test repository |
| ۱۲ | سیاست سازمانی token را تعیین کنید: fine-grained، expiration اجباری، owner، purpose، review cycle و revoke-on-role-change. | Security + IT | policy published |
| ۱۳ | branch protection/ruleset را فعال کنید: PR review، required checks، restricted tag creation و CODEOWNERS برای `.github/workflows/**`. | Repo admin | screenshot/config export یا ruleset ID |
| ۱۴ | incident retrospective انجام دهید و P0 اقدام‌های بازمانده را با owner/date ثبت کنید. | Security + Product | signed-off retrospective |

---

## ۲. معماری credential پیشنهادی

| نیاز | روش مجاز | روش ممنوع |
|---|---|---|
| انتشار GitHub Release | `GITHUB_TOKEN` کم‌مجوز فقط در release job با protected Environment | PAT انسانی در repository/org secret یا remote URL |
| GitHub integration در product | GitHub App با installation token کوتاه‌عمر؛ OAuth برای user consent | PAT classic با scope گسترده و بدون expiry |
| CI به cloud signing / artifact store | OIDC federation با trust policy محدود به repo/ref/environment | access key بلندمدت در GitHub Secret |
| CLI محلی | environment injection کوتاه‌عمر یا OS credential store | `--token` در command line، shell history یا commit |
| Desktop Windows | Credential Manager/Credential Locker | QSettings، JSON، SQLite، `.env` product file |

GitHub توصیه می‌کند برای tokenها expiration تعریف شود. [1] GitHub App یا OIDC جایگزین بهتری برای credentialهای انسانی و بلندمدت هستند، زیرا blast radius و چرخهٔ rotation را کاهش می‌دهند.

---

## ۳. اصلاح معماری workflow

### وضعیت فعلی که باید اصلاح شود

workflow فعلی `contents: write` را در سطح کل workflow اعطا می‌کند، از action tagهای mutable استفاده می‌کند، dependency range بدون lock/hash نصب می‌کند، EXE امضانشده می‌سازد و در همان job release را منتشر می‌کند. این ترکیب یک failure در build یا dependency را به publication permission متصل می‌کند.

### الگوی هدف: Validate → Build → Sign → Publish

| Job | Permissions | Trust boundary | خروجی |
|---|---|---|---|
| Validate | `contents: read` | build/test بدون secret و بدون deploy | test report، lint، secret scan |
| Build | `contents: read` | artifact ساختنی، بدون credential انتشار | unsigned artifact، SBOM، checksums |
| Sign | OIDC فقط برای signing service یا protected secret | protected Environment و approval | signed artifact + verification report |
| Publish | `contents: write` فقط در release job | protected Environment، tag policy، approval | GitHub Release با signed asset و hashes |

### Reference workflow — الگوی امن، نه فایل آمادهٔ فعال‌سازی

این مثال باید با SHAهای action تأییدشده و policy سازمان شما بازبینی شود. SHAهای زیر در ۱۴ اوت ۲۰۲۶ از repositoryهای عمومی actionها resolve شده‌اند؛ پیش از استفادهٔ production، provenance و commit را دوباره verify کنید.

```yaml
name: Build and Release Windows

on:
  push:
    tags: ["v*"]
  workflow_dispatch:

# deny by default
permissions: {}

jobs:
  validate:
    runs-on: windows-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
        with:
          python-version: "3.11"
      - name: Install locked dependencies
        run: python -m pip install --require-hashes -r requirements.lock
      - name: Test and scan
        run: |
          python -m unittest discover -s tests -v
          # add secret scan, ruff/mypy and dependency audit here

  build:
    needs: validate
    runs-on: windows-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
        with:
          python-version: "3.11"
      - name: Build reproducibly
        run: |
          python -m pip install --require-hashes -r requirements.lock
          pyinstaller --noconfirm --clean --onefile --windowed --name AI-Code-Reviewer-Enterprise --add-data "rules;rules" --add-data "translations;translations" app.py
          Get-FileHash dist/AI-Code-Reviewer-Enterprise.exe -Algorithm SHA256 | Format-List
      - name: Upload unsigned build for signing
        # use immutable upload-artifact action SHA after independent verification
        run: echo "Upload artifact to the protected signing stage"

  publish:
    needs: build
    runs-on: windows-latest
    environment: production-release
    permissions:
      contents: write
      id-token: write # only if the signing/publishing service uses OIDC
    steps:
      - name: Download, sign, and verify artifact
        run: |
          # Sign via managed signing service / HSM-backed certificate.
          # Verify Authenticode signature and compare checksum.
          echo "Sign and verify here"
      - name: Publish verified release
        uses: softprops/action-gh-release@3bb12739c298aeb8a4eeaf626c5b8d85266b0e65
        with:
          files: |
            dist/AI-Code-Reviewer-Enterprise.exe
            dist/AI-Code-Reviewer-Enterprise.exe.sha256
            dist/sbom.cdx.json
```

GitHub می‌گوید pin کردن action به full-length commit SHA تنها راه استفاده از release immutable است؛ action tag—even با creator معتبر—قابل جابه‌جایی است. [2] به‌دلیل این‌که actionهای third-party هم dependency هستند، باید برای update آن‌ها Dependabot و human review فعال شود.

---

## ۴. CI/CD Hardening Checklist

| کنترل | اجرای مشخص | وضعیت هدف |
|---|---|---|
| Least privilege | `permissions: {}` در workflow و permission حداقلی per job | اجباری |
| Immutable actions | SHA pin برای هر `uses:`؛ SHA از repository اصلی verify شود | اجباری |
| Dependency integrity | lockfile/hash؛ `pip install --require-hashes`؛ update automation | اجباری |
| Secret protection | secret scan در PR/tag؛ redaction test؛ ممنوعیت secret در `run:` interpolation | اجباری |
| Branch/tag governance | ruleset، required reviews/checks، CODEOWNERS برای workflows، restricted release tags | اجباری |
| Protected release | Environment با required reviewer و approval | اجباری |
| Artifact integrity | Authenticode signing، SBOM، SHA-256، verification قبل از upload | اجباری برای commercial release |
| Build separation | build job هیچ `contents: write` یا publish secret ندارد | اجباری |
| Cloud auth | OIDC trust constrained to repository + tag + Environment | اجباری در صورت cloud signing |
| Audit | release, environment approval, workflow-change و secret event review | اجباری |

### تنظیمات repository/organisation

در GitHub Actions settings، default `GITHUB_TOKEN` را به read-only محدود کنید و فقط workflow release permission لازم را به‌صورت job-level افزایش دهد. اجازهٔ اجرای workflow از fork را بدون approval و بدون secrets حفظ نکنید. `pull_request_target` را برای build/untrusted checkout به‌کار نبرید. برای self-hosted runner، آن را از public repository و untrusted PR جدا نگه دارید؛ runner ephemeral و network-egress محدود ترجیح دارد.

---

## ۵. verification و پاسخ به incident

پس از revoke، با یک درخواست API کم‌خطر یا `git fetch` تأیید کنید که token سابق دیگر کار نمی‌کند؛ خود secret را در command یا log چاپ نکنید. هر credential جایگزین با least-privilege scope و expiration مستند می‌شود. سپس security/audit log را از زمان نخستین exposure تا زمان revoke مرور کنید. نبود رویداد مشکوک، امکان abuse را اثباتاً رد نمی‌کند؛ اما به تعیین دامنهٔ incident کمک می‌کند.

اگر token در commit عمومی وجود داشته، history rewrite و cache removal ممکن است لازم باشد؛ پیش از این کار branch protection، backup، ارتباط با contributors و هماهنگی با forkها ضروری است. حتی پس از rewrite، revoke همچنان کنترل اصلی است، چون cloneها، forkها، logها یا screenshotها ممکن است باقی بمانند.

---

## منابع

[1]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation "GitHub Docs — Token expiration and revocation"
[2]: https://docs.github.com/en/actions/reference/security/secure-use "GitHub Docs — Secure use reference"

---

## افشا و حدود

**مبنا:** این راهنما از ممیزی workflow فعلی و مستندات رسمی GitHub تهیه شده است.  
**زمان:** action SHAها و منابع در ۱۴ اوت ۲۰۲۶ بررسی شده‌اند.  
**فرض‌ها:** repository روی GitHub است و انتشار EXE از GitHub Actions انجام می‌شود.  
**منابع و اطمینان:** گردش revoke و hardening مبنای رسمی GitHub دارد؛ integration دقیق signing/OIDC باید با cloud provider و policy سازمان validate شود.  
**انطباق:** این سند یک runbook فنی است و جایگزین incident-response، forensic یا مشاورهٔ امنیتی قراردادی نیست.

---
**Prepared by Manus AI**
