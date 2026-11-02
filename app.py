from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from analyzer import AnalysisError, analyze_csv_bytes

BASE_DIR = Path(__file__).resolve().parent
MAX_FILE_SIZE = 5 * 1024 * 1024

app = FastAPI(title="DataGuard", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        return {"error": "CSV 파일만 업로드할 수 있습니다."}
    data = await file.read()
    if len(data) == 0:
        return {"error": "빈 파일은 분석할 수 없습니다."}
    if len(data) > MAX_FILE_SIZE:
        return {"error": "파일 크기는 최대 5MB까지 허용됩니다."}
    try:
        return analyze_csv_bytes(data)
    except AnalysisError as exc:
        return {"error": str(exc)}
    except Exception:
        return {"error": "CSV 분석 중 오류가 발생했습니다. 파일 형식과 인코딩을 확인해주세요."}

