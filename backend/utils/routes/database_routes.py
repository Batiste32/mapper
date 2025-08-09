from fastapi import UploadFile, File, APIRouter, Depends
import pandas as pd
from backend.utils.constants import DATABASE_PATH, CSV_PATH

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
async def upload_db(file: UploadFile = File(...)):
    file_path = DATABASE_PATH
    with open(file_path, "wb") as f:
        f.write(await file.read())

    current_files["db"] = str(file_path)
    return {"status": "success", "path": str(file_path)}
