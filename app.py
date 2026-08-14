import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.ai_engine import AIEngine
from core.github_client import GitHubClient
from core.i18n import SUPPORTED_LOCALES, install_translation, normalize_locale
from core.license_manager import LicenseManager
from core.telemetry import Telemetry
from ui.main_window import MainWindow


SUPPORTED_REVIEW_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".cpp", ".cc", ".cxx", ".rs"}


def run_gui(token, locale="auto"):
    app = QApplication(sys.argv)
    selected_locale = normalize_locale(locale)
    translator = install_translation(app, selected_locale)
    github_client = GitHubClient(token)
    ai_engine = AIEngine()
    license_mgr = LicenseManager()
    telemetry = Telemetry()
    
    window = MainWindow(github_client, ai_engine, license_mgr, telemetry)
    window.selected_locale = selected_locale
    window.translation_active = translator is not None
    window.show()
    sys.exit(app.exec())


def run_cli(token, owner, repo, pull_number, sarif_output=None, rule_pack_path=None):
    """Run a PR review and optionally write a local SARIF artifact for CI integration."""
    github_client = GitHubClient(token)
    ai_engine = AIEngine(rule_pack_path=rule_pack_path or None)

    print(f"[*] Starting AI Review for {owner}/{repo} PR #{pull_number}...")
    files = github_client.get_pull_request_files(owner, repo, pull_number)
    all_issues = []

    for file in files if isinstance(files, list) else []:
        filename = file["filename"]
        if Path(filename).suffix.lower() not in SUPPORTED_REVIEW_EXTENSIONS:
            continue

        print(f"[*] Reviewing {filename}...")
        content = github_client.get_file_content(owner, repo, filename)
        if not content:
            continue

        review = ai_engine.analyze_code(content, filename)
        for notice in review.get("analysis_metadata", {}).get("rule_pack_notices", []):
            print(f"[!] Rule-pack notice for {filename}: {notice}")
        for issue in review.get("issues", []):
            issue["file"] = filename
            issue["language"] = issue.get("language", review.get("language", "unknown"))
            all_issues.append(issue)

    if sarif_output:
        output = ai_engine.export_sarif(
            all_issues,
            sarif_output,
            artifact_uri=f"{owner}/{repo}",
            run_category="ai-code-reviewer-cli",
        )
        print(f"[+] Local SARIF artifact written: {output}")

    if all_issues:
        summary = ai_engine.generate_summary(len(all_issues), f"{owner}/{repo}")
        report = f"### AI-Code-Reviewer Enterprise Report\n\n{summary}\n\n#### Summary of Findings:\n"
        for issue in all_issues:
            report += (
                f"- **[{issue.get('severity', 'Low')}] {issue.get('category', 'Bug')} · "
                f"{issue.get('rule_id', 'ACR-UNCLASSIFIED')}** in "
                f"`{issue.get('file', 'file')}:{issue.get('line', '1')}` - "
                f"{issue.get('description', '')}\n"
            )
            report += f"  - *Suggestion:* {issue.get('suggestion', '')}\n"

        github_client.post_comment(owner, repo, pull_number, report)
        print("[+] Review posted successfully!")
    else:
        github_client.post_comment(owner, repo, pull_number, "AI Review: No major issues found. Great job!")
        print("[+] No issues found. Review posted.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Code-Reviewer Enterprise")
    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--owner", help="Repository owner")
    parser.add_argument("--repo", help="Repository name")
    parser.add_argument("--pr", type=int, help="Pull request number")
    parser.add_argument(
        "--locale",
        default="auto",
        choices=["auto", *sorted(SUPPORTED_LOCALES)],
        help="Desktop display language: auto, en, or fa. Only bundled and reviewed translations are loaded.",
    )
    parser.add_argument(
        "--sarif-output",
        help="Optional local output path for SARIF 2.1.0 results. The application does not upload this file automatically.",
    )
    parser.add_argument(
        "--rule-pack",
        help="Optional local JSON-only Enterprise Rule Pack path. Invalid packs are reported as notices and do not stop local SAST.",
    )

    args = parser.parse_args()

    if args.cli:
        if not (args.owner and args.repo and args.pr):
            parser.error("--owner, --repo, and --pr are required with --cli")
        run_cli(args.token, args.owner, args.repo, args.pr, args.sarif_output, args.rule_pack)
    else:
        run_gui(args.token, args.locale)
