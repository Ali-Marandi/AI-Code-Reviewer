import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QListWidget, QTextEdit, 
    QStackedWidget, QFrame, QLineEdit, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPalette
import qtawesome as qta

class MainWindow(QMainWindow):
    def __init__(self, github_client, ai_engine):
        super().__init__()
        self.github = github_client
        self.ai = ai_engine
        self.setWindowTitle("AI-Code-Reviewer Enterprise")
        self.resize(1200, 800)
        
        # Apply Dark Theme
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QWidget { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Segoe UI', sans-serif; }
            QFrame#Sidebar { background-color: #252526; border-right: 1px solid #333; }
            QPushButton { 
                background-color: transparent; 
                border: none; 
                text-align: left; 
                padding: 10px 20px; 
                font-size: 14px; 
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #37373d; }
            QPushButton#Active { background-color: #37373d; border-left: 3px solid #007acc; }
            QListWidget { background-color: #252526; border: 1px solid #333; border-radius: 5px; }
            QTextEdit { background-color: #1e1e1e; border: 1px solid #333; border-radius: 5px; padding: 10px; }
            QLineEdit { background-color: #3c3c3c; border: 1px solid #333; border-radius: 3px; padding: 5px; color: white; }
            QLabel#Title { font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(250)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        
        self.logo = QLabel("AI-Code-Reviewer")
        self.logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #007acc; margin: 20px 0;")
        self.sidebar_layout.addWidget(self.logo)

        self.btn_dashboard = QPushButton(qta.icon("fa5s.tachometer-alt"), " Dashboard")
        self.btn_repos = QPushButton(qta.icon("fa5s.code-branch"), " Repositories")
        self.btn_prs = QPushButton(qta.icon("fa5s.tasks"), " Pull Requests")
        self.btn_settings = QPushButton(qta.icon("fa5s.cog"), " Settings")

        self.sidebar_layout.addWidget(self.btn_dashboard)
        self.sidebar_layout.addWidget(self.btn_repos)
        self.sidebar_layout.addWidget(self.btn_prs)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.btn_settings)

        self.layout.addWidget(self.sidebar)

        # Main Content
        self.content_stack = QStackedWidget()
        self.layout.addWidget(self.content_stack)

        # Pages
        self.init_dashboard()
        self.init_repos()
        self.init_settings()

        # Connections
        self.btn_dashboard.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        self.btn_repos.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        self.btn_settings.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))

    def init_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Enterprise Dashboard")
        title.setObjectName("Title")
        layout.addWidget(title)

        stats_layout = QHBoxLayout()
        for label in ["Total PRs: 0", "Issues Found: 0", "Security Risks: 0"]:
            card = QFrame()
            card.setStyleSheet("background-color: #2d2d2d; border-radius: 10px; padding: 20px;")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(label))
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        self.content_stack.addWidget(page)

    def init_repos(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Your Repositories")
        title.setObjectName("Title")
        layout.addWidget(title)

        self.repo_list = QListWidget()
        layout.addWidget(self.repo_list)
        
        self.btn_refresh = QPushButton("Refresh Repositories")
        self.btn_refresh.clicked.connect(self.load_repos)
        layout.addWidget(self.btn_refresh)
        
        self.content_stack.addWidget(page)

    def init_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Settings")
        title.setObjectName("Title")
        layout.addWidget(title)

        layout.addWidget(QLabel("GitHub Personal Access Token:"))
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.token_input)

        layout.addWidget(QLabel("AI Model Selection:"))
        self.model_input = QLineEdit("gpt-5")
        layout.addWidget(self.model_input)

        save_btn = QPushButton("Save Settings")
        layout.addWidget(save_btn)
        layout.addStretch()
        
        self.content_stack.addWidget(page)

    def load_repos(self):
        self.repo_list.clear()
        try:
            repos = self.github.get_repositories()
            for repo in repos:
                item = QListWidgetItem(repo['full_name'])
                self.repo_list.addItem(item)
        except Exception as e:
            self.repo_list.addItem(f"Error: {str(e)}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # Dummy clients for testing
    window = MainWindow(None, None)
    window.show()
    sys.exit(app.exec())
