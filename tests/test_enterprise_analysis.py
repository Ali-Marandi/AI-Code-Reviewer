import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from core.ai_engine import AIEngine


class EnterpriseAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "review_cache.db")
        os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used-for-local-tests")
        self.engine = AIEngine(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_rule_pack_detects_multi_language_shell_patterns(self):
        samples = [
            ("danger.py", "import subprocess\nsubprocess.run(command, shell=True)\n", "ACR-PY-SHELL-TRUE"),
            ("Danger.java", 'new ProcessBuilder("bash", "-c", command).start();\n', "ACR-JAVA-SHELL-C"),
            ("danger.go", 'exec.Command("sh", "-c", command).Run()\n', "ACR-GO-SHELL-C"),
            ("danger.rs", 'Command::new("bash").arg("-c").arg(command).status();\n', "ACR-RUST-SHELL-C"),
        ]
        for file_path, code, expected_rule_id in samples:
            with self.subTest(file_path=file_path):
                issues = self.engine.run_local_sast(code, file_path)
                self.assertIn(expected_rule_id, {issue["rule_id"] for issue in issues})

    def test_invalid_rule_pack_does_not_stop_local_scan(self):
        invalid_pack = Path(self.temp_dir.name) / "invalid_rules.json"
        invalid_pack.write_text('{"schema_version": 99, "rules": []}', encoding="utf-8")
        engine = AIEngine(db_path=str(Path(self.temp_dir.name) / "invalid.db"), rule_pack_path=str(invalid_pack))

        issues = engine.run_local_sast('api_key = "this-is-a-long-secret-value"\n', "settings.py")

        self.assertTrue(issues)
        self.assertTrue(any("schema_version" in notice for notice in engine._latest_rule_pack_notices))

    def test_sarif_contains_rule_location_and_fingerprint(self):
        issue = {
            "file": "src/unsafe.py",
            "line": 7,
            "severity": "High",
            "category": "Security",
            "description": "Unsafe dynamic execution.",
            "suggestion": "Use a safe parser.",
            "rule_id": "ACR-PY-DYNAMIC-EXECUTION",
            "source": "local_sast",
            "language": "python",
        }
        sarif = self.engine.build_sarif([issue], artifact_uri="fallback")
        run = sarif["runs"][0]
        result = run["results"][0]

        self.assertEqual(sarif["version"], "2.1.0")
        self.assertEqual(result["ruleId"], "ACR-PY-DYNAMIC-EXECUTION")
        self.assertEqual(result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"], "src/unsafe.py")
        self.assertEqual(result["locations"][0]["physicalLocation"]["region"]["startLine"], 7)
        self.assertIn("primaryLocationLineHash", result["partialFingerprints"])
        self.assertEqual(run["tool"]["driver"]["rules"][0]["id"], "ACR-PY-DYNAMIC-EXECUTION")

    def test_history_persists_metadata_without_source_code(self):
        source_code = "def sensitive_internal_implementation():\n    return 'do-not-store-this-code'\n"
        issues = self.engine.run_local_sast(source_code, "internal.py")
        self.engine._record_review_history(issues, "internal.py", "python")

        summary = self.engine.get_history_summary(30)
        self.assertEqual(summary["scans"], 1)

        with sqlite3.connect(self.db_path) as connection:
            history_columns = [row[1] for row in connection.execute("PRAGMA table_info(scan_history)")]
            stored_values = " ".join(str(row) for row in connection.execute("SELECT * FROM scan_history").fetchall())
        self.assertNotIn("code", history_columns)
        self.assertNotIn("do-not-store-this-code", stored_values)

    def test_export_sarif_writes_valid_json(self):
        output = Path(self.temp_dir.name) / "results.sarif"
        path = self.engine.export_sarif(
            [
                {
                    "file": "src/main.go",
                    "line": 3,
                    "severity": "Medium",
                    "category": "Security",
                    "description": "Review command construction.",
                    "suggestion": "Use explicit arguments.",
                    "rule_id": "ACR-GO-SHELL-C",
                    "source": "custom_rule_pack",
                    "language": "go",
                }
            ],
            str(output),
            artifact_uri="fallback",
        )
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "2.1.0")
        self.assertEqual(payload["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"], "src/main.go")


if __name__ == "__main__":
    unittest.main()
