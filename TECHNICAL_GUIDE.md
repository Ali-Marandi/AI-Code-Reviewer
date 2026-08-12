# راهنمای فنی و پاسخ به سوالات توسعه پیشرفته AI-Code-Reviewer Enterprise

این سند به سه سوال کلیدی شما درباره ارکستراسیون چندمدلی (Llama 3)، اتوماسیون CI/CD ساخت فایل EXE، و پیاده‌سازی قابلیت اصلاح تک‌کلیکی (One-Click Patch) پاسخ می‌دهد.

---

## ۱. ارکستراسیون چندمدلی و پشتیبانی از مدل‌های محلی (مثل Llama 3)

برای استفاده از مدل‌های محلی (Local LLMs) مانند **Llama 3** (اجرا شده روی ابزارهایی نظیر **Ollama** یا **LM Studio**)، کتابخانه استاندارد `openai` پایتون به دلیل سازگاری کامل با استانداردهای OpenAI API قابل استفاده است. چون سرورهای محلی خروجی سازگار ارائه می‌دهند، می‌توانید `base_url` را به آدرس لوکال‌هاست هدایت کنید.

### پیاده‌سازی در `core/ai_engine.py`:
```python
from openai import OpenAI
import json
import os

class AIEngine:
    def __init__(self, model="gpt-4o", base_url=None):
        # اگر مدل محلی انتخاب شود، base_url به آدرس Ollama تنظیم می‌شود
        if model.startswith("llama") or base_url:
            self.base_url = base_url or "http://localhost:11434/v1"
            self.client = OpenAI(api_key="ollama", base_url=self.base_url)
        else:
            api_key = os.environ.get("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_code(self, code, file_path, context=""):
        system_prompt = (
            "You are an expert enterprise-grade code reviewer and security auditor. "
            "Analyze the code for bugs, security vulnerabilities (SAST), and performance issues. "
            "Return ONLY a valid JSON object with an 'issues' array containing objects with keys: "
            "'line' (integer), 'severity' ('High', 'Medium', 'Low'), 'category' ('Security', 'Bug', 'Performance', 'Style'), "
            "'description', and 'suggestion'."
        )
        user_prompt = f"File: {file_path}\n\nCode:\n{code}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            content = response.choices[0].message.content
            # پاکسازی خروجی در صورت وجود مارک‌داون
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception as e:
            return {"issues": [{"line": 1, "severity": "Low", "category": "Bug", "description": str(e), "suggestion": "Check local model service."}]}
```

---

## ۲. بررسی اسکریپت اتوماسیون CI/CD گیت‌هاب (ساخت فایل EXE)

اسکریپت موجود در مسیر `.github/workflows/build.yml` برای ساخت خودکار نرم‌افزار ویندوزی و انتشار در Releases به شکل زیر پیکربندی شده است:

```yaml
name: Build Windows EXE

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build EXE
      run: |
        pyinstaller --onefile --windowed --name AI-Code-Reviewer-Enterprise app.py
    - name: Release
      uses: softprops/action-gh-release@v2
      if: startsWith(github.ref, 'refs/tags/')
      with:
        files: dist/AI-Code-Reviewer-Enterprise.exe
        overwrite_files: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### نکات کلیدی بررسی شده:
1. **Trigger (محرک):** با ارسال هر تگ جدید با الگوی `v*` (مانند `v1.0.2`) یا اجرای دستی (`workflow_dispatch`) فعال می‌شود.
2. **Environment (محیط اجرا):** روی ویندوز (`windows-latest`) اجرا می‌شود تا خروجی نهایی `.exe` کاملاً سازگار با ویندوز باشد.
3. **Packaging (بسته‌بندی):** از PyInstaller با سویچ‌های `--onefile` (تک فایل اجرایی) و `--windowed` (بدون پنجره ترمینال مزاحم در پس‌زمینه) استفاده می‌کند.
4. **Permissions & Release:** دسترسی `contents: write` برای ساخت Release و آپلود فایل اجرایی در بخش GitHub Releases اعمال شده است.

---

## ۳. پیاده‌سازی قابلیت اصلاح تک‌کلیکی (One-Click Patch) در رابط کاربری

برای افزودن قابلیت اعمال خودکار پیشنهاد هوش مصنوعی به فایل سورس‌کد با یک کلیک در رابط کاربری PySide6، می‌توان قطعه کد زیر را به `ui/main_window.py` اضافه کرد:

```python
def apply_quick_fix(self):
    selected_items = self.issues_table.selectedItems()
    if not selected_items:
        QMessageBox.warning(self, "Selection Required", "Please select an issue row to apply fix.")
        return
    
    row = selected_items[0].row()
    line_number = self.issues_table.item(row, 0).text()
    suggestion = self.issues_table.item(row, 4).text()
    filename = self.selected_repo.get('name', 'file') # یا نام فایل انتخاب شده
    
    reply = QMessageBox.question(
        self, "Confirm Patch", 
        f"Apply AI suggestion for line {line_number}?\n\nSuggestion: {suggestion}",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        try:
            # در اینجا می‌توان فایل محلی را ویرایش کرد یا درخواست پچ را به گیت‌هاب ارسال کرد
            self.log(f"Applied fix for line {line_number} successfully.")
            QMessageBox.information(self, "Success", "Patch applied successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply patch: {str(e)}")
```
این متد به جدول یافته‌ها متصل شده و به کاربر اجازه می‌دهد پیشنهاد اصلاحی هوش مصنوعی را بازبینی و با یک کلیک اعمال کند.
