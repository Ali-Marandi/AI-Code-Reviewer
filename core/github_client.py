import requests
import base64

class GitHubClient:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"

    def get_user_info(self):
        response = requests.get(f"{self.base_url}/user", headers=self.headers)
        return response.json()

    def get_repositories(self):
        response = requests.get(f"{self.base_url}/user/repos?per_page=100", headers=self.headers)
        return response.json()

    def get_pull_requests(self, owner, repo):
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_pull_request_files(self, owner, repo, pull_number):
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/files"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def post_comment(self, owner, repo, pull_number, body):
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pull_number}/comments"
        data = {"body": body}
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def get_file_content(self, owner, repo, path, ref="main"):
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            content = response.json().get("content", "")
            return base64.b64decode(content).decode("utf-8")
        return None
