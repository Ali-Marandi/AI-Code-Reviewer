import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used-for-ui-smoke-test")

from PySide6.QtWidgets import QApplication

from core.ai_engine import AIEngine
from ui.main_window import MainWindow


class DummyGitHubClient:
    pass


def main():
    app = QApplication([])
    with tempfile.TemporaryDirectory() as directory:
        engine = AIEngine(db_path=os.path.join(directory, "ui_smoke.db"))
        window = MainWindow(DummyGitHubClient(), engine)
        assert window.content_stack.count() == 5
        assert window.btn_export_sarif.isEnabled() is False
        assert window.rule_pack_input.text().endswith("enterprise_default_rules.json")
        window.refresh_history()
        window.close()
    app.quit()
    print("UI smoke test passed")


if __name__ == "__main__":
    main()
