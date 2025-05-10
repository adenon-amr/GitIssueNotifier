import os

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
GITHUB_PAT = os.environ["TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

REPO_FILE = "repos.txt"
STATE_FILE = "last_checked.json"
