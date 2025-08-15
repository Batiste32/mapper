from fastapi import UploadFile, File, APIRouter, Depends
import pandas as pd
from backend.utils.constants import DATABASE_PATH, CSV_PATH
from backend.utils.google_drive import upload_user_db, get_user_db_path

# Will store paths in memory (per server process)
current_files = {
    "csv": None,
    "db": None
}

router = APIRouter()

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    file_path = CSV_PATH
    with open(file_path, "wb") as f:
        f.write(await file.read())

    current_files["csv"] = str(file_path)
    return {"status": "success", "path": str(file_path)}

@router.post("/upload_db")
async def upload_db(file: UploadFile, user_id: str=""):
    if user_id == "" :
        print("No User passed in upload_db")
        return {"status": "error"}
    
    temp_path = f"/tmp/{user_id}.db"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    upload_user_db(user_id, temp_path)

    db_path = get_user_db_path(user_id)
    return {"status": "success", "path": db_path}


async def old_upload_db(file: UploadFile = File(...)):
    file_path = DATABASE_PATH
    with open(file_path, "wb") as f:
        f.write(await file.read())

    current_files["db"] = str(file_path)
    return {"status": "success", "path": str(file_path)}
