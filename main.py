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

def send_email(subject, issue):
    title = issue["title"]
    body_text = issue["body"] or "No description provided."
    url = issue["html_url"]

    html_body = f"""
    <html>
    <body style="margin: 0; padding: 0; background-color: #f4f4f7; font-family: 'Segoe UI', sans-serif;">
        <div style="max-width: 600px; margin: 40px auto; background-color: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden;">
            <div style="background-color: #24292e; padding: 16px;">
                <h2 style="color: white; margin: 0;">GitSignal</h2>
            </div>
            <div style="padding: 32px; text-align: center;">
                <h1 style="font-size: 24px; color: #333333;">{title}</h1>
                <p style="font-size: 16px; color: #555555; text-align: left; line-height: 1.5; white-space: pre-wrap;">
                    {body_text}
                </p>
                <div style="margin-top: 30px;">
                    <a href="{url}" style="background-color: #2ea44f; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        View Issue on GitHub
                    </a>
                </div>
            </div>
            <div style="padding: 16px; text-align: center; background-color: #f9f9f9; font-size: 12px; color: #888888;">
                Powered by <strong>GitSignal</strong>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg["Subject"] = subject

    part = MIMEText(html_body, "html")
    msg.attach(part)

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
        if not send_email(subject, issue):
            success = False

    if success:
        save_last_checked(now)
        print(f"Updated last_checked to {now.isoformat()}")

if __name__ == "__main__":
    main()
