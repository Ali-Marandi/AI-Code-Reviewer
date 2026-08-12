from datetime import datetime, timedelta, timezone
from pathlib import Path
from openai import OpenAI
import ast
import hashlib
import json
import os
import re
import sqlite3
import uuid
from typing import Any, Dict, List, Optional, Tuple


class AIEngine:
    """
    Enterprise AI Code Reviewer engine.

    The engine keeps analysis local wherever possible and adds three enterprise
    controls: safe JSON rule packs, privacy-minimised trend history, and SARIF
    2.1.0 export. Rule packs never execute user-provided code; they only define
    validated regular-expression checks.
    """

    ANALYSIS_SCHEMA_VERSION = "2"
    SARIF_VERSION = "2.1.0"
    TOOL_NAME = "AI-Code-Reviewer Enterprise"
    VALID_SEVERITIES = {"Critical", "High", "Medium", "Low", "Info"}
    LANGUAGE_BY_EXTENSION = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
    }

    def __init__(
        self,
        model: str = "gpt-4o",
        db_path: str = "review_cache.db",
        rule_pack_path: Optional[str] = None,
    ):
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_API_BASE")
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)

        self.model = model
        self.db_path = db_path
        default_rule_pack = Path(__file__).resolve().parent.parent / "rules" / "enterprise_default_rules.json"
        self.rule_pack_path = str(Path(rule_pack_path).expanduser()) if rule_pack_path else str(default_rule_pack)
        self._init_cache_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_cache_db(self) -> None:
        """Create local-only cache and history stores without storing source code."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS review_cache (
                        code_hash TEXT PRIMARY KEY,
                        review_result TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scan_history (
                        scan_id TEXT PRIMARY KEY,
                        scanned_at TEXT NOT NULL,
                        file_hash TEXT NOT NULL,
                        language TEXT NOT NULL,
                        issue_count INTEGER NOT NULL,
                        high_or_critical_count INTEGER NOT NULL,
                        rule_pack_ref TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS finding_observations (
                        observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scan_id TEXT NOT NULL,
                        scanned_at TEXT NOT NULL,
                        fingerprint TEXT NOT NULL,
                        rule_id TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        category TEXT NOT NULL,
                        line_number INTEGER NOT NULL,
                        FOREIGN KEY(scan_id) REFERENCES scan_history(scan_id)
                    )
                    """
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_scan_history_scanned_at ON scan_history(scanned_at)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_finding_observations_scanned_at ON finding_observations(scanned_at)"
                )
        except sqlite3.Error:
            # History/cache loss must never block a review.
            pass

    @staticmethod
    def _get_hash(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def detect_language(self, file_path: str) -> str:
        suffix = Path(file_path or "").suffix.lower()
        return self.LANGUAGE_BY_EXTENSION.get(suffix, "unknown")

    def _rule_pack_signature(self) -> str:
        """Return a cache-safe signature without reading user source code."""
        try:
            rule_path = Path(self.rule_pack_path).expanduser().resolve()
            stat = rule_path.stat()
            return f"{rule_path}:{stat.st_mtime_ns}:{stat.st_size}"
        except OSError:
            return f"missing:{self.rule_pack_path}"

    def _review_cache_key(self, code: str, file_path: str) -> str:
        payload = "|".join(
            [
                self.ANALYSIS_SCHEMA_VERSION,
                file_path or "",
                self._rule_pack_signature(),
                code,
            ]
        )
        return self._get_hash(payload)

    @staticmethod
    def _line_number_for_offset(code: str, offset: int) -> int:
        return code.count("\n", 0, max(offset, 0)) + 1

    @classmethod
    def _normalise_severity(cls, severity: Any) -> str:
        candidate = str(severity or "Low").strip().title()
        return candidate if candidate in cls.VALID_SEVERITIES else "Low"

    def _normalise_issue(
        self,
        issue: Dict[str, Any],
        *,
        language: str,
        source: str,
        fallback_rule_id: str,
    ) -> Dict[str, Any]:
        try:
            line = max(int(issue.get("line", 1)), 1)
        except (TypeError, ValueError):
            line = 1

        return {
            "line": line,
            "severity": self._normalise_severity(issue.get("severity")),
            "category": str(issue.get("category") or "Bug"),
            "description": str(issue.get("description") or "Review finding."),
            "suggestion": str(issue.get("suggestion") or "Review the finding in context."),
            "rule_id": str(issue.get("rule_id") or fallback_rule_id),
            "source": str(issue.get("source") or source),
            "language": str(issue.get("language") or language),
        }

    def _load_rule_pack(self) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, str]]:
        """Load a JSON-only rule pack, rejecting executable or malformed content."""
        notices: List[str] = []
        metadata = {"path": self.rule_pack_path, "name": "Unavailable", "version": "unknown"}
        valid_rules: List[Dict[str, Any]] = []

        try:
            rule_path = Path(self.rule_pack_path).expanduser()
            if rule_path.suffix.lower() != ".json":
                raise ValueError("Rule pack must be a .json file.")
            if not rule_path.is_file():
                raise FileNotFoundError("Rule pack file does not exist.")
            if rule_path.stat().st_size > 1_000_000:
                raise ValueError("Rule pack is larger than the 1 MB local safety limit.")

            with rule_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)

            if not isinstance(payload, dict) or payload.get("schema_version") != 1:
                raise ValueError("Rule pack schema_version must be 1.")
            rules = payload.get("rules")
            if not isinstance(rules, list):
                raise ValueError("Rule pack must contain a rules array.")

            metadata = {
                "path": str(rule_path),
                "name": str(payload.get("name") or rule_path.stem),
                "version": str(payload.get("version") or "unknown"),
            }
            allowed_languages = set(self.LANGUAGE_BY_EXTENSION.values()) | {"all"}
            seen_rule_ids = set()

            for index, rule in enumerate(rules, start=1):
                if not isinstance(rule, dict):
                    notices.append(f"Rule #{index} ignored: a rule must be a JSON object.")
                    continue

                required = ("id", "pattern", "languages", "severity", "category", "description", "suggestion")
                if any(not isinstance(rule.get(field), str) and field != "languages" for field in required):
                    notices.append(f"Rule #{index} ignored: one or more required text fields are missing.")
                    continue
                if not isinstance(rule.get("languages"), list) or not rule["languages"]:
                    notices.append(f"Rule #{index} ignored: languages must be a non-empty array.")
                    continue

                rule_id = rule["id"].strip()
                pattern = rule["pattern"]
                languages = [str(language).strip().lower() for language in rule["languages"]]
                severity = self._normalise_severity(rule["severity"])
                if not rule_id or len(rule_id) > 160 or rule_id in seen_rule_ids:
                    notices.append(f"Rule #{index} ignored: id is blank, too long, or duplicated.")
                    continue
                if not pattern or len(pattern) > 1_000:
                    notices.append(f"Rule {rule_id} ignored: pattern is blank or too long.")
                    continue
                if any(language not in allowed_languages for language in languages):
                    notices.append(f"Rule {rule_id} ignored: unsupported language selector.")
                    continue

                flags = re.IGNORECASE if bool(rule.get("ignore_case", False)) else 0
                try:
                    compiled = re.compile(pattern, flags)
                except re.error as error:
                    notices.append(f"Rule {rule_id} ignored: invalid regular expression ({error}).")
                    continue

                valid_rules.append(
                    {
                        "id": rule_id,
                        "compiled_pattern": compiled,
                        "languages": languages,
                        "severity": severity,
                        "category": rule["category"].strip() or "Security",
                        "description": rule["description"].strip() or "Custom rule finding.",
                        "suggestion": rule["suggestion"].strip() or "Review the finding in context.",
                    }
                )
                seen_rule_ids.add(rule_id)

        except (OSError, ValueError, json.JSONDecodeError) as error:
            notices.append(f"Custom rule pack unavailable: {error}")

        return valid_rules, notices, metadata

    def _run_custom_rules(self, code: str, language: str) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, str]]:
        rules, notices, metadata = self._load_rule_pack()
        issues: List[Dict[str, Any]] = []

        for rule in rules:
            if "all" not in rule["languages"] and language not in rule["languages"]:
                continue
            try:
                for match in rule["compiled_pattern"].finditer(code):
                    issues.append(
                        {
                            "line": self._line_number_for_offset(code, match.start()),
                            "severity": rule["severity"],
                            "category": rule["category"],
                            "description": rule["description"],
                            "suggestion": rule["suggestion"],
                            "rule_id": rule["id"],
                            "source": "custom_rule_pack",
                            "language": language,
                        }
                    )
            except re.error as error:
                notices.append(f"Rule {rule['id']} failed during matching: {error}")

        return issues, notices, metadata

    def run_local_sast(self, code: str, file_path: str = "") -> List[Dict[str, Any]]:
        """Run conservative local checks and safe custom JSON rules without network access."""
        issues: List[Dict[str, Any]] = []
        language = self.detect_language(file_path)
        secret_patterns = [
            ("ACR-LOCAL-GITHUB-TOKEN", r"ghp_[a-zA-Z0-9]{36}", "Potential GitHub personal access token detected."),
            ("ACR-LOCAL-OPENAI-KEY", r"sk-[a-zA-Z0-9]{20,}", "Potential OpenAI-style API token detected."),
            ("ACR-LOCAL-API-KEY", r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "Potential hardcoded API key detected."),
        ]
        for rule_id, pattern, description in secret_patterns:
            for match in re.finditer(pattern, code, re.IGNORECASE):
                issues.append(
                    {
                        "line": self._line_number_for_offset(code, match.start()),
                        "severity": "High",
                        "category": "Security",
                        "description": description,
                        "suggestion": "Move credentials to an approved secret manager or environment variable, then rotate the exposed credential.",
                        "rule_id": rule_id,
                        "source": "local_sast",
                        "language": language,
                    }
                )

        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                        issues.append(
                            {
                                "line": getattr(node, "lineno", 1),
                                "severity": "High",
                                "category": "Security",
                                "description": f"Use of unsafe built-in function '{node.func.id}' detected.",
                                "suggestion": "Avoid dynamic code execution. Use an allowlisted parser or a safe, typed alternative.",
                                "rule_id": "ACR-PY-DYNAMIC-EXECUTION",
                                "source": "local_sast",
                                "language": language,
                            }
                        )
            except SyntaxError:
                # A syntax error is handled by AI review or external compilation; it should not hide regex findings.
                pass

        custom_issues, notices, _ = self._run_custom_rules(code, language)
        issues.extend(custom_issues)
        # Notices are deliberately returned separately in analyze_code so invalid configuration does not masquerade as code risk.
        self._latest_rule_pack_notices = notices
        return self._deduplicate_issues(issues)

    @staticmethod
    def _issue_fingerprint(issue: Dict[str, Any], file_path: str) -> str:
        stable = "|".join(
            [
                str(file_path or ""),
                str(issue.get("rule_id") or "ACR-UNCLASSIFIED"),
                str(issue.get("line") or 1),
                str(issue.get("category") or ""),
                str(issue.get("description") or ""),
            ]
        )
        return hashlib.sha256(stable.encode("utf-8")).hexdigest()

    def _deduplicate_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique: List[Dict[str, Any]] = []
        seen = set()
        for issue in issues:
            key = "|".join(
                [
                    str(issue.get("rule_id") or ""),
                    str(issue.get("line") or 1),
                    str(issue.get("severity") or ""),
                    str(issue.get("description") or ""),
                ]
            )
            if key not in seen:
                seen.add(key)
                unique.append(issue)
        return unique

    def analyze_dependency_graph(self, code: str, file_path: str = "") -> Dict[str, List[str]]:
        imports: List[str] = []
        functions: List[str] = []
        if self.detect_language(file_path) not in {"python", "unknown"}:
            return {"imports": imports, "defined_functions": functions}
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
        except SyntaxError:
            pass
        return {"imports": sorted(set(imports)), "defined_functions": sorted(set(functions))}

    def predict_bugs(self, code: str, file_path: str = "") -> List[str]:
        predictions: List[str] = []
        if self.detect_language(file_path) not in {"python", "unknown"}:
            return predictions
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    has_return = any(isinstance(child, ast.Return) for child in ast.walk(node))
                    if not has_return and node.name != "__init__":
                        predictions.append(
                            f"Function '{node.name}' has no return statement. It may return None unexpectedly."
                        )
        except SyntaxError:
            pass
        return predictions

    def _load_cached_review(self, cache_key: str) -> Optional[Dict[str, Any]]:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT review_result FROM review_cache WHERE code_hash = ?", (cache_key,)
                ).fetchone()
            return json.loads(row["review_result"]) if row else None
        except (sqlite3.Error, json.JSONDecodeError, TypeError):
            return None

    def _cache_review(self, cache_key: str, data: Dict[str, Any]) -> None:
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO review_cache (code_hash, review_result) VALUES (?, ?)",
                    (cache_key, json.dumps(data)),
                )
        except (sqlite3.Error, TypeError):
            pass

    def _record_review_history(self, issues: List[Dict[str, Any]], file_path: str, language: str) -> None:
        """Persist metadata and hashes only; source code and snippets are never written to history."""
        try:
            scan_id = str(uuid.uuid4())
            scanned_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            file_hash = self._get_hash(str(file_path or ""))
            high_or_critical = sum(
                1 for issue in issues if issue.get("severity") in {"High", "Critical"}
            )
            rule_pack_ref = self._rule_pack_signature()
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO scan_history (
                        scan_id, scanned_at, file_hash, language, issue_count,
                        high_or_critical_count, rule_pack_ref
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        scan_id,
                        scanned_at,
                        file_hash,
                        language,
                        len(issues),
                        high_or_critical,
                        rule_pack_ref,
                    ),
                )
                conn.executemany(
                    """
                    INSERT INTO finding_observations (
                        scan_id, scanned_at, fingerprint, rule_id, severity, category, line_number
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            scan_id,
                            scanned_at,
                            self._issue_fingerprint(issue, file_path),
                            str(issue.get("rule_id") or "ACR-UNCLASSIFIED"),
                            str(issue.get("severity") or "Low"),
                            str(issue.get("category") or "Bug"),
                            int(issue.get("line") or 1),
                        )
                        for issue in issues
                    ],
                )
        except (sqlite3.Error, ValueError, TypeError):
            pass

    def get_findings_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Return daily aggregate metadata for local dashboard use, without source-code content."""
        bounded_days = min(max(int(days), 1), 365)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=bounded_days - 1)).date().isoformat()
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT substr(scanned_at, 1, 10) AS day,
                           COUNT(DISTINCT scan_id) AS scans,
                           SUM(issue_count) AS findings,
                           SUM(high_or_critical_count) AS high_or_critical
                    FROM scan_history
                    WHERE substr(scanned_at, 1, 10) >= ?
                    GROUP BY substr(scanned_at, 1, 10)
                    ORDER BY day ASC
                    """,
                    (cutoff,),
                ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error:
            return []

    def get_history_summary(self, days: int = 30) -> Dict[str, int]:
        bounded_days = min(max(int(days), 1), 365)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=bounded_days - 1)).date().isoformat()
        summary = {"scans": 0, "findings": 0, "high_or_critical": 0, "unique_fingerprints": 0}
        try:
            with self._connect() as conn:
                scan_row = conn.execute(
                    """
                    SELECT COUNT(*) AS scans,
                           COALESCE(SUM(issue_count), 0) AS findings,
                           COALESCE(SUM(high_or_critical_count), 0) AS high_or_critical
                    FROM scan_history
                    WHERE substr(scanned_at, 1, 10) >= ?
                    """,
                    (cutoff,),
                ).fetchone()
                fingerprint_row = conn.execute(
                    """
                    SELECT COUNT(DISTINCT fingerprint) AS unique_fingerprints
                    FROM finding_observations
                    WHERE substr(scanned_at, 1, 10) >= ?
                    """,
                    (cutoff,),
                ).fetchone()
            if scan_row:
                summary.update({key: int(scan_row[key] or 0) for key in ("scans", "findings", "high_or_critical")})
            if fingerprint_row:
                summary["unique_fingerprints"] = int(fingerprint_row["unique_fingerprints"] or 0)
        except sqlite3.Error:
            pass
        return summary

    def analyze_code(self, code: str, file_path: str, context: str = "") -> Dict[str, Any]:
        language = self.detect_language(file_path)
        cache_key = self._review_cache_key(code, file_path)
        cached = self._load_cached_review(cache_key)
        if cached:
            cached["from_cache"] = True
            self._record_review_history(cached.get("issues", []), file_path, language)
            return cached

        local_issues = self.run_local_sast(code, file_path)
        rule_pack_notices = getattr(self, "_latest_rule_pack_notices", [])
        _, _, rule_pack_metadata = self._load_rule_pack()
        dependency_graph = self.analyze_dependency_graph(code, file_path)
        bug_predictions = self.predict_bugs(code, file_path)

        system_prompt = (
            "You are an expert enterprise-grade code reviewer and security auditor. "
            "Analyze the supplied code for bugs, security vulnerabilities, performance bottlenecks, "
            "and adherence to best practices. Provide structured JSON with an 'issues' array. "
            "Each issue must contain: line (integer), severity (Critical/High/Medium/Low/Info), "
            "category (Security/Bug/Performance/Style), description, and suggestion. "
            "Do not claim certainty when evidence is insufficient."
        )
        dependency_info = f"Dependencies: {dependency_graph['imports']}; functions: {dependency_graph['defined_functions']}"
        prediction_info = f"Local bug-prediction notices: {bug_predictions}"
        user_prompt = (
            f"File: {file_path}\nLanguage: {language}\n\nContext:\n{context}\n\n"
            f"{dependency_info}\n{prediction_info}\n\nCode to review:\n{code}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            if not isinstance(data, dict):
                data = {}
            raw_ai_issues = data.get("issues", []) if isinstance(data.get("issues", []), list) else []
            ai_issues = [
                self._normalise_issue(
                    issue if isinstance(issue, dict) else {},
                    language=language,
                    source="ai_review",
                    fallback_rule_id="ACR-AI-REVIEW",
                )
                for issue in raw_ai_issues
            ]
        except Exception as error:
            ai_issues = [
                {
                    "line": 1,
                    "severity": "Info",
                    "category": "Analysis",
                    "description": f"AI analysis unavailable: {str(error)}",
                    "suggestion": "Local SAST, custom rules, and AST analysis completed. Re-run with a configured AI provider when available.",
                    "rule_id": "ACR-AI-UNAVAILABLE",
                    "source": "engine_notice",
                    "language": language,
                }
            ]

        issues = self._deduplicate_issues(local_issues + ai_issues)
        data = {
            "issues": issues,
            "dependency_graph": dependency_graph,
            "bug_predictions": bug_predictions,
            "language": language,
            "from_cache": False,
            "analysis_metadata": {
                "schema_version": self.ANALYSIS_SCHEMA_VERSION,
                "rule_pack": rule_pack_metadata,
                "rule_pack_notices": rule_pack_notices,
            },
        }
        self._cache_review(cache_key, data)
        self._record_review_history(issues, file_path, language)
        return data

    @staticmethod
    def _sarif_level(severity: str) -> str:
        return {
            "Critical": "error",
            "High": "error",
            "Medium": "warning",
            "Low": "note",
            "Info": "note",
        }.get(severity, "warning")

    def build_sarif(
        self,
        issues: List[Dict[str, Any]],
        *,
        artifact_uri: str,
        run_category: str = "ai-code-reviewer-local",
    ) -> Dict[str, Any]:
        """Build a SARIF 2.1.0 document without embedding source code or secrets."""
        rules: Dict[str, Dict[str, Any]] = {}
        results: List[Dict[str, Any]] = []
        for issue in issues:
            normalised = self._normalise_issue(
                issue,
                language=str(issue.get("language") or self.detect_language(artifact_uri)),
                source=str(issue.get("source") or "unknown"),
                fallback_rule_id="ACR-UNCLASSIFIED",
            )
            rule_id = normalised["rule_id"]
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "name": rule_id,
                    "shortDescription": {"text": normalised["description"][:300]},
                    "defaultConfiguration": {"level": self._sarif_level(normalised["severity"])},
                    "properties": {
                        "severity": normalised["severity"],
                        "category": normalised["category"],
                        "source": normalised["source"],
                    },
                }
            issue_artifact_uri = str(issue.get("file") or artifact_uri)
            fingerprint = self._issue_fingerprint(normalised, issue_artifact_uri)
            results.append(
                {
                    "ruleId": rule_id,
                    "level": self._sarif_level(normalised["severity"]),
                    "message": {"text": normalised["description"]},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": issue_artifact_uri},
                                "region": {"startLine": normalised["line"]},
                            }
                        }
                    ],
                    "partialFingerprints": {"primaryLocationLineHash": fingerprint},
                    "properties": {
                        "severity": normalised["severity"],
                        "category": normalised["category"],
                        "suggestion": normalised["suggestion"],
                        "language": normalised["language"],
                        "source": normalised["source"],
                    },
                }
            )

        return {
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "version": self.SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.TOOL_NAME,
                            "informationUri": "https://github.com/Ali-Marandi/AI-Code-Reviewer",
                            "rules": list(rules.values()),
                        }
                    },
                    "automationDetails": {"id": run_category},
                    "results": results,
                }
            ],
        }

    def export_sarif(
        self,
        issues: List[Dict[str, Any]],
        output_path: str,
        *,
        artifact_uri: str,
        run_category: str = "ai-code-reviewer-local",
    ) -> str:
        """Write a local SARIF artifact. Uploading or posting remains an explicit user action."""
        target = Path(output_path).expanduser()
        if target.suffix.lower() not in {".sarif", ".json"}:
            target = target.with_suffix(".sarif")
        target.parent.mkdir(parents=True, exist_ok=True)
        sarif = self.build_sarif(issues, artifact_uri=artifact_uri, run_category=run_category)
        with target.open("w", encoding="utf-8") as handle:
            json.dump(sarif, handle, indent=2, ensure_ascii=False)
        return str(target)

    def generate_summary(self, issues_count: int, repo_name: str) -> str:
        try:
            prompt = (
                f"Summarize an enterprise code review for repository {repo_name} which found "
                f"{issues_count} issues. Highlight security and code-quality posture in two or three professional sentences."
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
            )
            return response.choices[0].message.content or "Review completed."
        except Exception:
            return f"Review completed with {issues_count} total findings across repository files."
