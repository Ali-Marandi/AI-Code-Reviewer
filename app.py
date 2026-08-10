import sys
import argparse
from PySide6.QtWidgets import QApplication
from core.github_client import GitHubClient
from core.ai_engine import AIEngine
from ui.main_window import MainWindow

def run_gui(token):
    app = QApplication(sys.argv)
    github_client = GitHubClient(token)
    ai_engine = AIEngine()
    window = MainWindow(github_client, ai_engine)
    window.show()
    sys.exit(app.exec())

def run_cli(token, owner, repo, pull_number):
    github_client = GitHubClient(token)
    ai_engine = AIEngine()
    
    print(f"[*] Starting AI Review for {owner}/{repo} PR #{pull_number}...")
    files = github_client.get_pull_request_files(owner, repo, pull_number)
    
    all_issues = []
    for file in files:
        filename = file['filename']
        if not filename.endswith(('.py', '.js', '.ts', '.go', '.java', '.cpp')):
            continue
            
        print(f"[*] Reviewing {filename}...")
        content = github_client.get_file_content(owner, repo, filename)
        if content:
            review = ai_engine.analyze_code(content, filename)
            if 'issues' in review:
                for issue in review['issues']:
                    issue['file'] = filename
                    all_issues.append(issue)

    if all_issues:
        summary = ai_engine.generate_summary(len(all_issues), f"{owner}/{repo}")
        report = f"### AI Code Review Summary\n\n{summary}\n\n#### Found Issues:\n"
        for issue in all_issues:
            report += f"- **[{issue['severity']}]** {issue['file']}:{issue['line']} - {issue['description']}\n"
            report += f"  - *Suggestion:* {issue['suggestion']}\n"
        
        github_client.post_comment(owner, repo, pull_number, report)
        print("[+] Review posted successfully!")
    else:
        github_client.post_comment(owner, repo, pull_number, "✅ AI Review: No major issues found. Great job!")
        print("[+] No issues found. Review posted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Code-Reviewer Enterprise")
    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--owner", help="Repo owner")
    parser.add_argument("--repo", help="Repo name")
    parser.add_argument("--pr", type=int, help="Pull request number")
    
    args = parser.parse_args()
    
    if args.cli:
        if not (args.owner and args.repo and args.pr):
            print("Error: --owner, --repo, and --pr are required for CLI mode.")
            sys.exit(1)
        run_cli(args.token, args.owner, args.repo, args.pr)
    else:
        run_gui(args.token)
