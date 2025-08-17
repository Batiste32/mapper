import os, json, requests, hashlib
from backend.utils.constants import USER_SESSION_PATH

DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

def get_dropbox_access_token():
    """Get a fresh Dropbox API access token using refresh token"""
    resp = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": DROPBOX_REFRESH_TOKEN,
        },
        auth=(DROPBOX_APP_KEY, DROPBOX_APP_SECRET),
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def upload_to_dropbox(local_path: str, dropbox_path: str):
    token = get_dropbox_access_token()
    with open(local_path, "rb") as f:
        data = f.read()

    resp = requests.post(
        "https://content.dropboxapi.com/2/files/upload",
        headers={
            "Authorization": f"Bearer {token}",
            "Dropbox-API-Arg": json.dumps({
                "path": dropbox_path,
                "mode": "overwrite",  # overwrite if exists
                "autorename": False
            }),
            "Content-Type": "application/octet-stream",
        },
        data=data,
    )
    resp.raise_for_status()
    return resp.json()

def download_from_dropbox(dropbox_path: str, local_path: str):
    token = get_dropbox_access_token()

    resp = requests.post(
        "https://content.dropboxapi.com/2/files/download",
        headers={
            "Authorization": f"Bearer {token}",
            "Dropbox-API-Arg": json.dumps({"path": dropbox_path}),
        },
    )
    resp.raise_for_status()

    with open(local_path, "wb") as f:
        f.write(resp.content)

    return local_path

def load_user_sessions():
    local_path = "/tmp/user_session.json"
    try:
        download_from_dropbox(USER_SESSION_PATH, local_path)
        with open(local_path, "r") as f:
            return json.load(f)
    except:
        return {}  # empty if file doesn't exist yet

def save_user_sessions(sessions: dict):
    local_path = "/tmp/user_session.json"
    with open(local_path, "w") as f:
        json.dump(sessions, f, indent=2)
    upload_to_dropbox(local_path, USER_SESSION_PATH)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def user_login(username: str, password: str):
    sessions = load_user_sessions()
    hashed = hash_password(password)

    if username not in sessions:
        raise ValueError("User not found")

    if sessions[username]["hashed_password"] != hashed:
        raise ValueError("Invalid password")

    last_db = sessions[username]["last_db"]
    if last_db:
        local_db = f"/tmp/{username}.db"
        download_from_dropbox(last_db, local_db)
        return local_db
    return None

def user_upload_db(username: str, password: str, local_db_path: str):
    sessions = load_user_sessions()
    hashed = hash_password(password)

    if username not in sessions:
        # Register new user
        sessions[username] = {"hashed_password": hashed, "last_db": None}
    elif sessions[username]["hashed_password"] != hashed:
        raise ValueError("Invalid password")

    dropbox_path = f"/databases/{username}.db"
    upload_to_dropbox(local_db_path, dropbox_path)

    sessions[username]["last_db"] = dropbox_path
    save_user_sessions(sessions)