import os

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
GITHUB_PAT = os.environ["TOKEN"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

REPO_FILE = "repos.txt"
STATE_FILE = "last_checked.json"
