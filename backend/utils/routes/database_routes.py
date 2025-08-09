from fastapi import UploadFile, File, APIRouter, Depends
import sqlite3
import pandas as pd
import tempfile

router = APIRouter()

@router.post("/upload_db")
async def upload_db(file: UploadFile = File(...)):
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        contents = await file.read()
        tmp.write(contents)
        db_path = tmp.name

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return {"status": "success", "tables": tables}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    return {"columns": df.columns.tolist(), "preview": df.head(5).to_dict(orient="records")}