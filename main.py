import requests
import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

GITHUB_TOKEN = os.environ["TOKEN"]
REPOSITORIES = [
    "adithya-menon-r/test",
    "CSE-25/quick_start_express"
]

# Track the last time the script ran
last_run_time = time.time() - 3600  # Defaults to one hour ago for the first run

def get_new_issues():
    global last_run_time
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    new_issues = []
    current_time = time.time()

    for repo in REPOSITORIES:
        url = f"https://api.github.com/repos/{repo}/issues"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            issues = response.json()
            for issue in issues:
                issue_created_time = time.mktime(time.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"))
                if issue["state"] == "open" and issue_created_time > last_run_time:
                    new_issues.append(issue)

    last_run_time = current_time  # Update the last run time
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
    print("Monitoring GitHub repositories for new issues...")
    while True:
        new_issues = get_new_issues()
        for issue in new_issues:
            subject = f"New Issue in {issue['repository_url'].split('/')[-1]}: {issue['title']}"
            body = f"{issue['title']}\n\n{issue['body']}\n\nURL: {issue['html_url']}"
            send_email(subject, body)
        
        # Wait for 30 minutes before checking again
        time.sleep(1800)

if __name__ == "__main__":
    main()
