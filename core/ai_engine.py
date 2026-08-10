from openai import OpenAI
import json

class AIEngine:
    def __init__(self, model="gpt-5"):
        self.client = OpenAI()
        self.model = model

    def analyze_code(self, code, file_path, context=""):
        system_prompt = (
            "You are an expert enterprise-grade code reviewer. "
            "Analyze the following code for bugs, security vulnerabilities, performance issues, and adherence to best practices. "
            "Provide your feedback in a structured JSON format with the following fields: "
            "'issues' (a list of objects with 'line', 'severity' (High, Medium, Low), 'category' (Security, Bug, Performance, Style), 'description', and 'suggestion')."
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
                    "type": "json_schema",
                    "json_schema": {
                        "name": "code_review",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "issues": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "line": {"type": "integer"},
                                            "severity": {"type": "string", "enum": ["High", "Medium", "Low"]},
                                            "category": {"type": "string", "enum": ["Security", "Bug", "Performance", "Style"]},
                                            "description": {"type": "string"},
                                            "suggestion": {"type": "string"}
                                        },
                                        "required": ["line", "severity", "category", "description", "suggestion"],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": ["issues"],
                            "additionalProperties": False
                        }
                    }
                }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e), "issues": []}

    def generate_summary(self, issues_count, repo_name):
        prompt = f"Summarize a code review for repository {repo_name} which found {issues_count} issues. Keep it professional and encouraging."
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
