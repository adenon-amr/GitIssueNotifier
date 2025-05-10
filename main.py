from datetime import datetime, timezone
from utils import get_last_checked, save_last_checked, load_repos
from github_checker import get_new_issues
from emailer import send_new_issue_email

def main():
    print("Checking for new issues in tracked repos...")
    last_checked = get_last_checked()
    now = datetime.now(timezone.utc).replace(microsecond=0)

    repos = load_repos()
    new_issues = get_new_issues(last_checked, repos)

    success = True
    for issue in new_issues:
        if not send_new_issue_email(issue):
            success = False

    if success:
        save_last_checked(now)
        print(f"Updated last_checked.json to {now.isoformat()}")

if __name__ == "__main__":
    main()
