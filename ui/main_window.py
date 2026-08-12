import sys
import base64
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTextEdit,
    QStackedWidget, QFrame, QLineEdit, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QProgressBar, QSplitter, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont
import qtawesome as qta

class WorkerThread(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self, github_client, ai_engine):
        super().__init__()
        self.github = github_client
        self.ai = ai_engine
        self.selected_repo = None
        self.selected_pr = None
        self.last_review_issues = []
        self.last_review_context = {}
        self.review_history_days = 30

        self.setWindowTitle(self.tr("AI-Code-Reviewer Enterprise Edition v1.1.0"))
        self.resize(1300, 850)

        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QWidget { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
            QFrame#Sidebar { background-color: #252526; border-right: 1px solid #333; }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3f3f46;
                color: #ffffff;
                text-align: center;
                padding: 8px 16px;
                font-size: 13px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #38383d; border-color: #007acc; }
            QPushButton#SidebarBtn {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 12px 20px;
                font-size: 14px;
                border-radius: 0px;
            }
            QPushButton#SidebarBtn:hover { background-color: #2a2d2e; }
            QPushButton#SidebarBtn[active="true"] { background-color: #37373d; border-left: 3px solid #007acc; color: #ffffff; }
            QListWidget { background-color: #252526; border: 1px solid #333; border-radius: 4px; padding: 5px; }
            QListWidget::item { padding: 8px; border-radius: 3px; }
            QListWidget::item:hover { background-color: #2a2d2e; }
            QListWidget::item:selected { background-color: #37373d; color: #ffffff; }
            QTextEdit, QTableWidget { background-color: #1e1e1e; border: 1px solid #333; border-radius: 4px; gridline-color: #333; }
            QHeaderView::section { background-color: #2d2d2d; color: #ffffff; padding: 6px; border: 1px solid #333; font-weight: bold; }
            QLineEdit, QComboBox { background-color: #3c3c3c; border: 1px solid #555; border-radius: 3px; padding: 6px; color: white; }
            QLabel#Title { font-size: 22px; font-weight: bold; color: #ffffff; margin-bottom: 10px; }
            QLabel#Subtitle { font-size: 14px; color: #9cdcfe; margin-bottom: 15px; }
            QProgressBar { border: 1px solid #333; border-radius: 3px; text-align: center; background: #2d2d2d; color: white; }
            QProgressBar::chunk { background-color: #007acc; }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)

        logo_label = QLabel(self.tr("  AI-Code-Reviewer\n  Enterprise v1.1.0"))
        logo_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0; padding: 20px 15px; background-color: #1f1f20;")
        self.sidebar_layout.addWidget(logo_label)

        self.nav_buttons = []
        self.btn_dashboard = self.add_nav_btn(self.tr(" Dashboard"), "fa5s.tachometer-alt", 0, active=True)
        self.btn_repos = self.add_nav_btn(self.tr(" Repositories"), "fa5s.code-branch", 1)
        self.btn_prs = self.add_nav_btn(self.tr(" Pull Requests & Review"), "fa5s.tasks", 2)
        self.btn_history = self.add_nav_btn(self.tr(" Findings Trend"), "fa5s.chart-line", 3)
        self.btn_settings = self.add_nav_btn(self.tr(" Settings"), "fa5s.cog", 4)

        self.sidebar_layout.addStretch()

        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 15, 15, 15)
        self.lbl_status = QLabel(self.tr("Status: Ready"))
        self.lbl_status.setStyleSheet("color: #4ec9b0; font-size: 12px;")
        status_layout.addWidget(self.lbl_status)
        self.sidebar_layout.addWidget(status_frame)

        self.layout.addWidget(self.sidebar)

        # Main Content Stack
        self.content_stack = QStackedWidget()
        self.layout.addWidget(self.content_stack)

        self.init_dashboard_page()
        self.init_repos_page()
        self.init_prs_page()
        self.init_history_page()
        self.init_settings_page()

    def add_nav_btn(self, text, icon_name, index, active=False):
        btn = QPushButton(qta.icon(icon_name, color="#d4d4d4"), text)
        btn.setObjectName("SidebarBtn")
        btn.setProperty("active", "true" if active else "false")
        btn.clicked.connect(lambda: self.switch_page(index))
        self.sidebar_layout.addWidget(btn)
        self.nav_buttons.append(btn)
        return btn

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def init_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel(self.tr("Enterprise Dashboard"))
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel(self.tr("Overview of automated AI code reviews, security scans, and repository health."))
        subtitle.setObjectName("Subtitle")
        layout.addWidget(subtitle)

        stats_layout = QHBoxLayout()
        self.stat_repos = self.create_card(self.tr("Connected Repos"), "0")
        self.stat_prs = self.create_card(self.tr("Active PRs"), "0")
        self.stat_issues = self.create_card(self.tr("Findings in Last Review"), "0")
        self.stat_security = self.create_card(self.tr("Security Risk Level"), self.tr("Secure"))

        stats_layout.addWidget(self.stat_repos[0])
        stats_layout.addWidget(self.stat_prs[0])
        stats_layout.addWidget(self.stat_issues[0])
        stats_layout.addWidget(self.stat_security[0])
        layout.addLayout(stats_layout)

        activity_label = QLabel("Recent Activity & System Logs")
        activity_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px; color: #ffffff;")
        layout.addWidget(activity_label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("System logs and review outputs will appear here...")
        layout.addWidget(self.log_box)

        self.content_stack.addWidget(page)

    def create_card(self, title_text, value_text):
        card = QFrame()
        card.setStyleSheet("background-color: #252526; border: 1px solid #333; border-radius: 8px; padding: 20px;")
        vbox = QVBoxLayout(card)
        t_label = QLabel(title_text)
        t_label.setStyleSheet("color: #858585; font-size: 12px;")
        v_label = QLabel(value_text)
        v_label.setStyleSheet("color: #4ec9b0; font-size: 24px; font-weight: bold;")
        vbox.addWidget(t_label)
        vbox.addWidget(v_label)
        return card, v_label

    def init_repos_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel(self.tr("Repository Management"))
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel(self.tr("Select a repository to inspect pull requests and run enterprise AI audits."))
        subtitle.setObjectName("Subtitle")
        layout.addWidget(subtitle)

        self.repo_list = QListWidget()
        self.repo_list.itemClicked.connect(self.on_repo_selected)
        layout.addWidget(self.repo_list)

        btn_layout = QHBoxLayout()
        self.btn_load_repos = QPushButton(self.tr("Fetch Repositories from GitHub"))
        self.btn_load_repos.clicked.connect(self.fetch_repositories)
        btn_layout.addWidget(self.btn_load_repos)
        layout.addLayout(btn_layout)

        self.content_stack.addWidget(page)

    def init_prs_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel(self.tr("Pull Request Review & SAST Audit"))
        title.setObjectName("Title")
        layout.addWidget(title)

        self.lbl_selected_context = QLabel(self.tr("Current Repository: None Selected"))
        self.lbl_selected_context.setObjectName("Subtitle")
        layout.addWidget(self.lbl_selected_context)

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel(self.tr("Open Pull Requests:")))
        self.pr_list = QListWidget()
        self.pr_list.itemClicked.connect(self.on_pr_selected)
        left_layout.addWidget(self.pr_list)

        self.btn_fetch_prs = QPushButton(self.tr("Load PRs for Selected Repo"))
        self.btn_fetch_prs.clicked.connect(self.fetch_pull_requests)
        left_layout.addWidget(self.btn_fetch_prs)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_layout.addWidget(QLabel(self.tr("Audit Findings & Issues:")))
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(6)
        self.issues_table.setHorizontalHeaderLabels(["Line", "Severity", "Rule", "Category", "Description", "Suggestion"])
        self.issues_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.issues_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        right_layout.addWidget(self.issues_table)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        right_layout.addWidget(self.progress_bar)

        review_actions = QHBoxLayout()
        btn_run_review = QPushButton(self.tr("Run AI Enterprise Review & Post Comment"))
        btn_run_review.setStyleSheet("background-color: #007acc; font-weight: bold; padding: 10px;")
        btn_run_review.clicked.connect(self.run_ai_review)
        review_actions.addWidget(btn_run_review)

        self.btn_export_sarif = QPushButton(self.tr("Export SARIF"))
        self.btn_export_sarif.setToolTip("Save the current local review findings as a SARIF 2.1.0 file. This does not upload data anywhere.")
        self.btn_export_sarif.setEnabled(False)
        self.btn_export_sarif.clicked.connect(self.export_sarif)
        review_actions.addWidget(self.btn_export_sarif)
        right_layout.addLayout(review_actions)

        splitter.addWidget(right_widget)
        splitter.setSizes([400, 700])
        layout.addWidget(splitter)

        self.content_stack.addWidget(page)

    def init_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel(self.tr("Local Findings Trend"))
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel("Privacy-minimised local history. It stores scan metadata and hashed finding fingerprints, never source code or secrets.")
        subtitle.setObjectName("Subtitle")
        layout.addWidget(subtitle)

        summary_layout = QHBoxLayout()
        self.stat_history_scans = self.create_card("Scans (30 days)", "0")
        self.stat_history_findings = self.create_card("Findings (30 days)", "0")
        self.stat_history_high = self.create_card("High/Critical (30 days)", "0")
        self.stat_history_unique = self.create_card("Unique fingerprints (30 days)", "0")
        for card, _ in [self.stat_history_scans, self.stat_history_findings, self.stat_history_high, self.stat_history_unique]:
            summary_layout.addWidget(card)
        layout.addLayout(summary_layout)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["UTC Day", "Scans", "Findings", "High / Critical"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)

        refresh_history_btn = QPushButton("Refresh Local Trend")
        refresh_history_btn.clicked.connect(self.refresh_history)
        layout.addWidget(refresh_history_btn)
        layout.addStretch()

        self.content_stack.addWidget(page)
        self.refresh_history()

    def init_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel(self.tr("Enterprise Settings"))
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel(self.tr("Configure GitHub authentication, API tokens, and AI model parameters."))
        subtitle.setObjectName("Subtitle")
        layout.addWidget(subtitle)

        locale_note = QLabel(self.tr("Display language is selected at startup with --locale (en, fa, or auto). Restart after changing language."))
        locale_note.setObjectName("Subtitle")
        locale_note.setWordWrap(True)
        layout.addWidget(locale_note)

        layout.addWidget(QLabel("GitHub Personal Access Token:"))
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setPlaceholderText("Enter your GitHub PAT...")
        layout.addWidget(self.token_input)

        layout.addWidget(QLabel("AI Model Engine:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet"])
        layout.addWidget(self.model_combo)

        layout.addWidget(QLabel("Local Enterprise Rule Pack (JSON):"))
        rule_pack_layout = QHBoxLayout()
        self.rule_pack_input = QLineEdit(self.ai.rule_pack_path)
        self.rule_pack_input.setToolTip("Local JSON-only rule pack. Rules are validated and never execute code.")
        rule_pack_layout.addWidget(self.rule_pack_input)
        browse_rule_pack_btn = QPushButton("Browse")
        browse_rule_pack_btn.clicked.connect(self.choose_rule_pack)
        rule_pack_layout.addWidget(browse_rule_pack_btn)
        layout.addLayout(rule_pack_layout)

        save_btn = QPushButton("Save & Re-initialize Clients")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.content_stack.addWidget(page)

    def log(self, text):
        self.log_box.append(f"[*] {text}")

    def fetch_repositories(self):
        self.log("Fetching repositories from GitHub...")
        self.btn_load_repos.setEnabled(False)
        self.worker = WorkerThread(self.github.get_repositories)
        self.worker.finished.connect(self.on_repos_loaded)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()

    def on_repos_loaded(self, repos):
        self.repo_list.clear()
        self.btn_load_repos.setEnabled(True)
        if isinstance(repos, list):
            for repo in repos:
                item = QListWidgetItem(repo['full_name'])
                item.setData(Qt.UserRole, repo)
                self.repo_list.addItem(item)
            self.stat_repos[1].setText(str(len(repos)))
            self.log(f"Successfully loaded {len(repos)} repositories.")
            QMessageBox.information(self, "Success", f"Loaded {len(repos)} repositories successfully.")
        else:
            self.log(f"Error loading repos: {repos}")
            QMessageBox.warning(self, "API Error", f"Could not load repositories: {repos}")

    def on_repo_selected(self, item):
        repo_data = item.data(Qt.UserRole)
        self.selected_repo = repo_data
        self.lbl_selected_context.setText(f"Current Repository: {repo_data['full_name']}")
        self.log(f"Selected repository: {repo_data['full_name']}")
        self.switch_page(2)
        self.fetch_pull_requests()

    def fetch_pull_requests(self):
        if not self.selected_repo:
            QMessageBox.warning(self, "Warning", "Please select a repository first in the Repositories tab.")
            return
        owner = self.selected_repo['owner']['login']
        repo = self.selected_repo['name']
        self.log(f"Fetching Pull Requests for {owner}/{repo}...")
        self.worker = WorkerThread(self.github.get_pull_requests, owner, repo)
        self.worker.finished.connect(self.on_prs_loaded)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()

    def on_prs_loaded(self, prs):
        self.pr_list.clear()
        if isinstance(prs, list):
            for pr in prs:
                item = QListWidgetItem(f"PR #{pr['number']}: {pr['title']}")
                item.setData(Qt.UserRole, pr)
                self.pr_list.addItem(item)
            self.stat_prs[1].setText(str(len(prs)))
            self.log(f"Loaded {len(prs)} pull requests.")
        else:
            self.log(f"No PRs or error: {prs}")

    def on_pr_selected(self, item):
        self.selected_pr = item.data(Qt.UserRole)
        self.log(f"Selected PR #{self.selected_pr['number']}: {self.selected_pr['title']}")

    def run_ai_review(self):
        if not self.selected_repo or not self.selected_pr:
            QMessageBox.warning(self, "Selection Required", "Please select both a repository and a Pull Request.")
            return

        self.progress_bar.show()
        owner = self.selected_repo['owner']['login']
        repo = self.selected_repo['name']
        pr_number = self.selected_pr['number']

        self.log(f"Starting AI Enterprise Review for {owner}/{repo} PR #{pr_number}...")

        def execute_review():
            files = self.github.get_pull_request_files(owner, repo, pr_number)
            all_issues = []
            rule_pack_notices = []
            if isinstance(files, list):
                for file in files:
                    filename = file['filename']
                    if not filename.endswith(('.py', '.js', '.ts', '.go', '.java', '.cpp', '.rs')):
                        continue
                    content = self.github.get_file_content(owner, repo, filename)
                    if content:
                        review = self.ai.analyze_code(content, filename)
                        rule_pack_notices.extend(
                            f"Rule-pack notice for {filename}: {notice}"
                            for notice in review.get('analysis_metadata', {}).get('rule_pack_notices', [])
                        )
                        if 'issues' in review:
                            for issue in review['issues']:
                                issue['file'] = filename
                                issue['language'] = issue.get('language', review.get('language', 'unknown'))
                                all_issues.append(issue)
            return {"issues": all_issues, "rule_pack_notices": rule_pack_notices}

        self.worker = WorkerThread(execute_review)
        self.worker.finished.connect(self.on_review_finished)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()

    def on_review_finished(self, review_result):
        self.progress_bar.hide()
        self.issues_table.setRowCount(0)
        if isinstance(review_result, dict):
            all_issues = review_result.get("issues", [])
            for notice in review_result.get("rule_pack_notices", []):
                self.log(notice)
        else:
            all_issues = review_result
        self.last_review_issues = list(all_issues or [])
        self.stat_issues[1].setText(str(len(self.last_review_issues)))
        self.btn_export_sarif.setEnabled(bool(self.last_review_issues))
        self.refresh_history()

        if not self.last_review_issues:
            QMessageBox.information(self, "Review Complete", "No code issues detected! Great job.")
            self.log("Review completed: No issues found.")
            return

        self.issues_table.setRowCount(len(self.last_review_issues))
        for row, issue in enumerate(self.last_review_issues):
            self.issues_table.setItem(row, 0, QTableWidgetItem(str(issue.get('line', 'N/A'))))
            self.issues_table.setItem(row, 1, QTableWidgetItem(issue.get('severity', 'Low')))
            self.issues_table.setItem(row, 2, QTableWidgetItem(issue.get('rule_id', 'ACR-UNCLASSIFIED')))
            self.issues_table.setItem(row, 3, QTableWidgetItem(issue.get('category', 'Bug')))
            self.issues_table.setItem(row, 4, QTableWidgetItem(issue.get('description', '')))
            self.issues_table.setItem(row, 5, QTableWidgetItem(issue.get('suggestion', '')))

        self.log(f"Review completed successfully. Found {len(self.last_review_issues)} issues.")

        owner = self.selected_repo['owner']['login']
        repo = self.selected_repo['name']
        pr_number = self.selected_pr['number']

        summary = self.ai.generate_summary(len(self.last_review_issues), f"{owner}/{repo}")
        report = f"### AI-Code-Reviewer Enterprise Report\n\n{summary}\n\n#### Summary of Findings:\n"
        for issue in self.last_review_issues:
            report += f"- **[{issue.get('severity','Low')}] {issue.get('category','Bug')} · {issue.get('rule_id','ACR-UNCLASSIFIED')}** in `{issue.get('file','file')}:{issue.get('line','1')}` - {issue.get('description','')}\n"
            report += f"  - *Suggestion:* {issue.get('suggestion','')}\n"

        try:
            self.github.post_comment(owner, repo, pr_number, report)
            self.log("Successfully posted review report comment to GitHub PR!")
            QMessageBox.information(self, "Success", f"Review completed with {len(self.last_review_issues)} issues and posted to GitHub PR #{pr_number}!")
        except Exception as e:
            self.log(f"Failed to post comment to GitHub: {str(e)}")

    def export_sarif(self):
        if not self.last_review_issues:
            QMessageBox.warning(self, "No Findings", "Run a review with findings before exporting a SARIF artifact.")
            return

        suggested_name = "ai-code-reviewer-results.sarif"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save SARIF Results",
            suggested_name,
            "SARIF files (*.sarif);;JSON files (*.json)",
        )
        if not output_path:
            return

        repo_name = self.selected_repo['full_name'] if self.selected_repo else "local-review"
        self.progress_bar.show()
        self.export_worker = WorkerThread(
            self.ai.export_sarif,
            self.last_review_issues,
            output_path,
            artifact_uri=repo_name,
            run_category="ai-code-reviewer-local",
        )
        self.export_worker.finished.connect(self.on_sarif_exported)
        self.export_worker.error.connect(self.on_worker_error)
        self.export_worker.start()

    def on_sarif_exported(self, output_path):
        self.progress_bar.hide()
        self.log(f"SARIF artifact exported locally: {output_path}")
        QMessageBox.information(
            self,
            "SARIF Export Complete",
            "SARIF 2.1.0 results were saved locally. No data was uploaded automatically.",
        )

    def refresh_history(self):
        summary = self.ai.get_history_summary(self.review_history_days)
        self.stat_history_scans[1].setText(str(summary.get('scans', 0)))
        self.stat_history_findings[1].setText(str(summary.get('findings', 0)))
        self.stat_history_high[1].setText(str(summary.get('high_or_critical', 0)))
        self.stat_history_unique[1].setText(str(summary.get('unique_fingerprints', 0)))

        trend = self.ai.get_findings_trend(self.review_history_days)
        self.history_table.setRowCount(len(trend))
        for row, point in enumerate(trend):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(point.get('day', ''))))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(point.get('scans', 0))))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(point.get('findings', 0))))
            self.history_table.setItem(row, 3, QTableWidgetItem(str(point.get('high_or_critical', 0))))

    def choose_rule_pack(self):
        rule_pack_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Local Rule Pack",
            self.rule_pack_input.text().strip() or "",
            "JSON files (*.json)",
        )
        if rule_pack_path:
            self.rule_pack_input.setText(rule_pack_path)

    def on_worker_error(self, err_msg):
        self.progress_bar.hide()
        self.log(f"Error: {err_msg}")
        QMessageBox.critical(self, "Error", f"An error occurred: {err_msg}")

    def save_settings(self):
        token = self.token_input.text().strip()
        model = self.model_combo.currentText()
        rule_pack_path = self.rule_pack_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Warning", "Token cannot be empty.")
            return

        from core.github_client import GitHubClient
        from core.ai_engine import AIEngine
        self.github = GitHubClient(token)
        self.ai = AIEngine(model=model, rule_pack_path=rule_pack_path or None)
        self.refresh_history()
        self.log(f"Settings saved. Updated GitHub client, AI model {model}, and local rule-pack configuration.")
        QMessageBox.information(self, "Settings Saved", "Enterprise settings updated successfully.")
