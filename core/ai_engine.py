from openai import OpenAI
import json
import os

class AIEngine:
    def __init__(self, model="gpt-4o"):
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_API_BASE")
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_code(self, code, file_path, context=""):
        system_prompt = (
            "You are an expert enterprise-grade code reviewer and security auditor. "
            "Analyze the following code for bugs, security vulnerabilities (SAST), performance bottlenecks, and adherence to best practices. "
            "Provide your feedback in a structured JSON format with the following fields: "
            "'issues' (a list of objects with 'line' (integer), 'severity' ('High', 'Medium', 'Low'), "
            "'category' ('Security', 'Bug', 'Performance', 'Style'), 'description', and 'suggestion')."
        )
        
        user_prompt = f"File: {file_path}\n\nContext:\n{context}\n\nCode to review:\n{code}"
        
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
            return data
        except Exception as e:
            return {
                "issues": [
                    {
                        "line": 1,
                        "severity": "Low",
                        "category": "Bug",
                        "description": f"AI analysis notice or parsing error: {str(e)}",
                        "suggestion": "Verify code manually or re-run review."
                    }
                ]
            }

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
