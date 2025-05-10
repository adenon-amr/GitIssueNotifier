import requests
from datetime import datetime, timezone
from config import GITHUB_PAT

def get_new_issues(last_checked, repos):
    headers = {"Authorization": f"token {GITHUB_PAT}"}
    new_issues = []

    for repo in repos:
        url = f"https://api.github.com/repos/{repo}/issues"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            issues = response.json()
            for issue in issues:
                if "pull_request" in issue:
                    continue
                created = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if issue["state"] == "open" and created > last_checked:
                    new_issues.append(issue)
    return new_issues
