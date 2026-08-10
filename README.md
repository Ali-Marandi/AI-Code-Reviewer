# AI-Code-Reviewer Enterprise 🚀

**AI-Code-Reviewer Enterprise** is a commercial-grade, AI-powered code analysis platform designed for modern engineering teams. It integrates deep reasoning capabilities of Large Language Models (LLMs) with your GitHub workflow to catch bugs, security vulnerabilities, and logic errors before they reach production.

## ✨ Key Features

- 🧠 **Deep Logic Analysis**: Goes beyond syntax checking to understand business logic and identify complex bugs.
- 🛡️ **Security-First (SAST)**: Automated detection of secrets, SQL injection, XSS, and other OWASP vulnerabilities.
- 💻 **Windows Desktop App**: A beautiful, modern GUI for managing PRs, viewing code diffs, and configuring AI rules.
- ⚡ **Auto-Fix Suggestions**: One-click code suggestions to resolve identified issues instantly.
- 🔄 **CI/CD Integration**: Seamlessly works with GitHub Actions to automate reviews on every Pull Request.
- 📊 **Enterprise Dashboard**: Track code quality metrics, team performance, and security trends.

## 🛠️ Installation

### Desktop Application
Download the latest `.exe` from the [Releases](https://github.com/Ali-Marandi/AI-Code-Reviewer/releases) page.

### CLI / Development
1. Clone the repository:
   ```bash
   git clone https://github.com/Ali-Marandi/AI-Code-Reviewer.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## 🚀 Usage

### GUI Mode
Simply run `python app.py` to launch the enterprise dashboard. Enter your GitHub Personal Access Token in the settings to get started.

### CLI Mode (for CI/CD)
```bash
python app.py --cli --token YOUR_TOKEN --owner OWNER --repo REPO --pr PR_NUMBER
```

## 📜 License
Commercial License - All Rights Reserved.
