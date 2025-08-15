import os
import io
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

# Google Drive API settings
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PICKLE = 'token.pickle'  # stores user credentials after first login
CREDENTIALS_FILE = os.getenv("GOOGLE_OAUTH_CREDENTIALS_FILE", "credentials.json")
FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

if not FOLDER_ID:
    raise ValueError("Missing GOOGLE_DRIVE_FOLDER_ID environment variable")

def get_drive_service():
    """Authenticate via OAuth and return a Drive API service instance."""
    creds = None

    # Load token if exists
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, go through OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"OAuth credentials file not found: {CREDENTIALS_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for next run
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def upload_file(file_path, file_name=None):
    """Upload a generic file to the configured folder."""
    service = get_drive_service()
    file_name = file_name or os.path.basename(file_path)
    file_metadata = {"name": file_name, "parents": [FOLDER_ID]}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded file ID: {file.get('id')}")
    return file.get('id')

def download_file(file_id, dest_path):
    """Download a file by its Drive file ID."""
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download {int(status.progress() * 100)}%")
    print(f"Downloaded to {dest_path}")

def upload_user_db(user_id: str, file_path: str):
    """Upload or update a DB file for a specific user."""
    service = get_drive_service()

    # Check if file already exists
    query = f"'{FOLDER_ID}' in parents and name='{user_id}.db'"
    results = service.files().list(q=query, fields="files(id)").execute()
    items = results.get("files", [])

    media = MediaFileUpload(file_path, mimetype='application/x-sqlite3', resumable=True)

    if items:
        # Update existing file
        file_id = items[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Updated DB for {user_id}")
    else:
        # Create new file
        file_metadata = {"name": f"{user_id}.db", "parents": [FOLDER_ID]}
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Uploaded DB for {user_id} with ID: {file.get('id')}")

def download_user_db(user_id: str, dest_path: str):
    """Download the DB file for a given user."""
    service = get_drive_service()
    query = f"'{FOLDER_ID}' in parents and name='{user_id}.db'"
    results = service.files().list(q=query, fields="files(id)").execute()
    items = results.get("files", [])

    if not items:
        raise FileNotFoundError(f"No DB file found for user {user_id}")

    file_id = items[0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download {int(status.progress() * 100)}%.")
    print(f"DB for {user_id} downloaded to {dest_path}")

def get_user_db_path(user_id: str) -> str:
    """Download a user's DB to a temp location and return the path."""
    tmp_path = os.path.join("/tmp", f"{user_id}.db")  # works on Linux
    download_user_db(user_id, tmp_path)
    return tmp_path