import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload, MediaFileUpload

# Load service account credentials
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)

def upload_user_db(user_id: str, file_path: str):

    if not SERVICE_ACCOUNT_FILE or not FOLDER_ID:
        raise ValueError("Missing SERVICE_ACCOUNT_FILE or FOLDER_ID environment variable")

    """Upload a DB file to Google Drive for this user_id."""
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
        file_metadata = {
            "name": f"{user_id}.db",
            "parents": [FOLDER_ID]
        }

        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Uploaded DB for {user_id} with ID: {file.get('id')}")

def download_user_db(user_id: str, dest_path: str):
    """Download the DB file for this user_id to dest_path."""
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
    dest_path = f"/tmp/{user_id}.db"
    download_user_db(user_id, dest_path)
    return dest_path