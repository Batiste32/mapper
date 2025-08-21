import os, json, requests, hashlib
import secrets
import string
from backend.utils.constants import USER_SESSION_PATH
from backend.database import set_database_path
from backend.utils.mail import send_email

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
    print("Retrieved Dropbox access token")
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
    print(f"Uploaded {local_path} to {dropbox_path}")
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
    if resp.status_code != 200:
        print(f"Dropbox error: {resp.status_code} {resp.text}")
    resp.raise_for_status()

    with open(local_path, "wb") as f:
        f.write(resp.content)

    print(f"Downloaded file {dropbox_path} at {local_path}")
    return local_path

def load_user_sessions():
    local_path = "/tmp/user_session.json"
    try:
        download_from_dropbox(USER_SESSION_PATH, local_path)
        with open(local_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to retrieve {USER_SESSION_PATH} -> {local_path} file: {e}")
        return {} 

def save_user_sessions(sessions: dict):
    local_path = "/tmp/user_session.json"
    with open(local_path, "w") as f:
        json.dump(sessions, f, indent=2)
    upload_to_dropbox(local_path, USER_SESSION_PATH)

def hash_password(password: str) -> str:
    hashed = hashlib.sha256(password.encode()).hexdigest()
    print(f"Password : {password}\tHashed : {hashed}")
    return hashed

def register_user(username: str, password: str, mail:str):
    """Registers a new user with empty DB reference."""
    sessions = load_user_sessions()
    if username in sessions:
        raise ValueError("User already exists")

    hashed = hash_password(password)
    sessions[username] = {"mail":mail, "hashed_password": hashed, "last_db": None}
    save_user_sessions(sessions)
    print(f"Registered new user: {username}")

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
        set_database_path(local_db)
        return local_db
    return None

def reset_password(username: str, email: str) -> None:
    """
    Reset a user's password by username and email.
    Generates a temporary password, updates the session, and returns it via email.
    """
    sessions = load_user_sessions()

    # Find the user
    if username not in sessions :
        raise ValueError(f"Cannot find user {username}.")
    if sessions[username]["mail"] != email :
        raise ValueError(f"Email {email} doesn't match user {username}.")

    # Generate a temporary password
    alphabet = string.ascii_letters + string.digits
    temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))

    # Hash and update
    hashed = hash_password(temp_password)
    sessions[username]["hashed_password"] = hashed
    save_user_sessions(sessions)

    body = f"Dear {username},\nA password reset for your Mapper account has been requested.\nHere is your new password : {temp_password}.\nIf you didn't request such a change, please contact Batiste Augereau at batiste.augereau@grenoble-inp.org.\nThank you."
    send_email(email, "Mapper Password Reset", body)

    print(f"Password change :\n{username}")

def user_upload_db(username: str, password: str, local_db_path: str):
    sessions = load_user_sessions()
    hashed = hash_password(password)

    if username not in sessions:
        raise ValueError(f"{username} not found in {sessions}")

    if sessions[username]["hashed_password"] != hashed:
        raise ValueError("Invalid password")

    dropbox_path = f"/databases/{username}.db"
    upload_to_dropbox(local_db_path, dropbox_path)

    sessions[username]["last_db"] = dropbox_path
    save_user_sessions(sessions)
    print(f"Updated DB for {username} at {dropbox_path}")
    set_database_path(local_db_path)
