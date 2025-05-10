import os
import json
from datetime import datetime, timezone, timedelta
from config import STATE_FILE

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
    from config import REPO_FILE
    if os.path.exists(REPO_FILE):
        with open(REPO_FILE) as f:
            return [line.strip() for line in f if line.strip()]
    return []
