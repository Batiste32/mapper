from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.utils.dropbox import user_login, user_upload_db
from backend.utils.constants import CSV_PATH

router = APIRouter()

# Will store active session info in memory (per server process)
current_files = {
    "csv": None,
    "db": None
}

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    """
    Authenticate a user. If they already have a database on Dropbox,
    download it to /tmp/<username>.db and set current_files["db"].
    """
    try:
        local_db = user_login(username, password)
        if local_db:
            current_files["db"] = local_db
        return {"status": "success", "db_path": local_db}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file. This is session-local only, not Dropbox.
    """
    file_path = CSV_PATH
    with open(file_path, "wb") as f:
        f.write(await file.read())

    current_files["csv"] = str(file_path)
    return {"status": "success", "path": str(file_path)}

@router.post("/upload_db")
async def upload_db(
    username: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and register a SQLite database for a given user.
    Stores file in Dropbox and updates user_session.json.
    """
    # Save temporarily in /tmp
    temp_path = f"/tmp/{username}.db"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        user_upload_db(username, password, temp_path)
        current_files["db"] = temp_path
        return {"status": "success", "path": temp_path}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))