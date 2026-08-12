from openai import OpenAI
import json
import os
import re
import ast
import hashlib
import sqlite3
from typing import Dict, List, Any

class AIEngine:
    """
    Advanced Enterprise AI Code Reviewer Engine
    Features: OpenAI integration, Local SAST, Dependency Graph Analysis, AI Bug Prediction, and Context Caching.
    """
    def __init__(self, model="gpt-4o", db_path: str = "review_cache.db"):
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_API_BASE")
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        self.model = model
        self.db_path = db_path
        self._init_cache_db()

    def _init_cache_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_cache (
                    code_hash TEXT PRIMARY KEY,
                    review_result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _get_hash(self, code: str) -> str:
        return hashlib.sha256(code.encode('utf-8')).hexdigest()

    def run_local_sast(self, code: str) -> List[Dict[str, Any]]:
        issues = []
        secret_patterns = [
            r'ghp_[a-zA-Z0-9]{36}',
            r'sk-[a-zA-Z0-9]{48}',
            r'api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "line": 1,
                    "severity": "High",
                    "category": "Security",
                    "description": "Potential hardcoded API token or secret detected.",
                    "suggestion": "Move credentials to environment variables or secret manager."
                })

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append({
                            "line": getattr(node, 'lineno', 1),
                            "severity": "High",
                            "category": "Security",
                            "description": f"Use of unsafe built-in function '{node.func.id}' detected.",
                            "suggestion": "Avoid dynamic code execution for security robustness."
                        })
        except SyntaxError:
            pass

        return issues

    def analyze_dependency_graph(self, code: str) -> Dict[str, List[str]]:
        imports = []
        functions = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except SyntaxError:
            pass

        return {
            "imports": list(set(imports)),
            "defined_functions": list(set(functions))
        }

    def predict_bugs(self, code: str) -> List[str]:
        predictions = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                    if not has_return and node.name != "__init__":
                        predictions.append(f"Function '{node.name}' has no return statement. Might return None unexpectedly.")
        except SyntaxError:
            pass
        return predictions

    def analyze_code(self, code, file_path, context=""):
        code_hash = self._get_hash(code)
        
        # Check cache
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT review_result FROM review_cache WHERE code_hash = ?', (code_hash,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row[0])
        except Exception:
            pass

        # Run local SAST & advanced analysis
        local_issues = self.run_local_sast(code)
        dep_graph = self.analyze_dependency_graph(code)
        bug_predictions = self.predict_bugs(code)

        system_prompt = (
            "You are an expert enterprise-grade code reviewer and security auditor. "
            "Analyze the following code for bugs, security vulnerabilities (SAST), performance bottlenecks, and adherence to best practices. "
            "Provide your feedback in a structured JSON format with the following fields: "
            "'issues' (a list of objects with 'line' (integer), 'severity' ('High', 'Medium', 'Low'), "
            "'category' ('Security', 'Bug', 'Performance', 'Style'), 'description', and 'suggestion')."
        )
        
        dep_info = f"Dependencies: {dep_graph['imports']}, Functions: {dep_graph['defined_functions']}"
        pred_info = f"Bug Predictions: {bug_predictions}"
        user_prompt = f"File: {file_path}\n\nContext:\n{context}\n{dep_info}\n{pred_info}\n\nCode to review:\n{code}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={
                    "type": "json_object"
                }
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            if "issues" not in data:
                data["issues"] = []
            
            # Merge local SAST issues
            data["issues"].extend(local_issues)
            data["dependency_graph"] = dep_graph
            data["bug_predictions"] = bug_predictions
            
        except Exception as e:
            data = {
                "issues": local_issues + [
                    {
                        "line": 1,
                        "severity": "Low",
                        "category": "Bug",
                        "description": f"AI analysis API notice: {str(e)}",
                        "suggestion": "Local SAST and AST analysis completed successfully."
                    }
                ],
                "dependency_graph": dep_graph,
                "bug_predictions": bug_predictions
            }

        # Cache result
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO review_cache (code_hash, review_result) VALUES (?, ?)', 
                           (code_hash, json.dumps(data)))
            conn.commit()
            conn.close()
        except Exception:
            pass

        return data

    def generate_summary(self, issues_count, repo_name):
        try:
            prompt = f"Summarize an enterprise code review for repository {repo_name} which found {issues_count} issues. Highlight security and code quality posture in 2-3 professional sentences."
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Review completed with {issues_count} total findings across repository files."
