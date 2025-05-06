import os
import json
import smtplib
import requests
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
TOKEN = os.environ["TOKEN"]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

REPO_FILE = "repos.txt"
STATE_FILE = "last_checked.json"

def get_last_checked():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return datetime.fromisoformat(data["last_checked"].replace("Z", "+00:00"))
    else:
        return datetime.now(timezone.utc) - timedelta(hours=1)

def save_last_checked(ts: datetime):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_checked": ts.isoformat().replace("+00:00", "Z")}, f)

def load_repos():
    if os.path.exists(REPO_FILE):
        with open(REPO_FILE) as f:
            return [line.strip() for line in f if line.strip()]
    return []

def get_new_issues(since, repos):
    headers = {"Authorization": f"token {TOKEN}"}
    new_issues = []
    for repo in repos:
        url = f"https://api.github.com/repos/{repo}/issues"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            issues = response.json()
            for issue in issues:
                created = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if issue["state"] == "open" and created > since:
                    new_issues.append(issue)
    return new_issues

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, EMAIL, msg.as_string())
        print("Email sent.")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

def main():
    print("Checking for new GitHub issues...")
    last_checked = get_last_checked()
    now = datetime.now(timezone.utc).replace(microsecond=0)

    repos = load_repos()
    new_issues = get_new_issues(last_checked, repos)

    success = True
    for issue in new_issues:
        subject = f"[{issue['repository_url'].split('/')[-1]}] {issue['title']}"
        body = f"{issue['title']}\n\n{issue['body']}\n\n{issue['html_url']}"
        if not send_email(subject, body):
            success = False

    if success:
        save_last_checked(now)
        print(f"Updated last_checked to {now.isoformat()}")

if __name__ == "__main__":
    main()
