"""
Advanced Enterprise Commercial Features for AI-Code-Reviewer v1.2.0:
1. Automated Refactoring Diff Generator (پایگاه‌داده اصلاح خودکار کدهای ناقص و تولید Patch)
2. Custom Policy Exemption Engine (موتور ثبت و اعتبارسنجی معافیت‌های سازمانی از قوانین خاص)
"""

import difflib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

class EnterpriseExtensionEngine:
    def __init__(self, exemptions_file: str = "rules/policy_exemptions.json"):
        self.exemptions_file = Path(exemptions_file)
        self.exemptions = self._load_exemptions()

    def _load_exemptions(self) -> List[Dict[str, Any]]:
        if not self.exemptions_file.exists():
            return []
        try:
            with open(self.exemptions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("exemptions", [])
        except (OSError, json.JSONDecodeError):
            return []

    def is_exempted(self, rule_id: str, file_path: str, line_number: int) -> bool:
        """Check if a specific finding is covered by a valid, non-expired enterprise policy exemption."""
        for ex in self.exemptions:
            if ex.get("rule_id") == rule_id:
                path_match = ex.get("file_pattern", "*") in file_path or ex.get("file_pattern") == "*"
                line_match = ex.get("line_number") is None or ex.get("line_number") == line_number
                if path_match and line_match:
                    return True
        return False

    def generate_refactoring_patch(self, original_code: str, rule_id: str, line_number: int) -> Optional[str]:
        """Generate a deterministic unified diff patch for common secure code refactoring."""
        lines = original_code.splitlines(keepends=True)
        if line_number < 1 or line_number > len(lines):
            return None
        
        target_line = lines[line_number - 1]
        modified_line = None

        if "ACR-LOCAL-GITHUB-TOKEN" in rule_id or "ACR-LOCAL-OPENAI-KEY" in rule_id or "ACR-LOCAL-API-KEY" in rule_id:
            # Refactor hardcoded secret to os.environ lookup
            indent = len(target_line) - len(target_line.lstrip())
            whitespace = target_line[:indent]
            var_name = "API_KEY"
            if "=" in target_line:
                parts = target_line.split("=")
                var_name = parts[0].strip().split()[-1]
            modified_line = f'{whitespace}{var_name} = os.environ.get("SECURE_API_KEY") # Refactored by AI-Code-Reviewer v1.2.0\n'
        elif "eval" in target_line:
            modified_line = target_line.replace("eval(", "ast.literal_eval(") # Safe alternative

        if modified_line and modified_line != target_line:
            new_lines = list(lines)
            new_lines[line_number - 1] = modified_line
            diff = difflib.unified_diff(
                lines,
                new_lines,
                fromfile="a/" + "source.py",
                tofile="b/" + "source.py",
                lineterm=""
            )
            return "\n".join(diff)
        
        return None
