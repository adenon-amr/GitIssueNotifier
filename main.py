import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPOSITORIES = [
    "adithya-menon-r/test",
    "CSE-25/quick_start_express"
]

notified_issues = set()
initialised = False  # Flag to track the first run


def get_new_issues():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    new_issues = []

    for repo in REPOSITORIES:
        url = f"https://api.github.com/repos/{repo}/issues"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            issues = response.json()
            for issue in issues:
                if issue["state"] == "open" and issue["id"] not in notified_issues:
                    new_issues.append(issue)
                    notified_issues.add(issue["id"])

    return new_issues


def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, EMAIL, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def main():
    global initialised
    print("Monitoring GitHub repositories for new issues...")

    while True:
        new_issues = get_new_issues()

        # Skip email notifications on the first run
        if not initialised:
            print("Initial load complete. Issues recorded but no emails sent.")
            initialised = True
        else:
            for issue in new_issues:
                subject = f"New Issue in {issue['repository_url'].split('/')[-1]}: {issue['title']}"
                body = f"{issue['title']}\n\n{issue['body']}\n\nURL: {issue['html_url']}"
                send_email(subject, body)

        time.sleep(300)  # Check every 5 minutes


if __name__ == "__main__":
    main()
