import os
import uuid
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(...)):
    # Save uploaded file with a unique name
    ext = os.path.splitext(file.filename)[1]
    saved_name = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_name)

    content = await file.read()
    with open(saved_path, "wb") as f:
        f.write(content)

    # Read sheet names
    xf = pd.ExcelFile(saved_path)
    sheet_names = xf.sheet_names

    return templates.TemplateResponse("partials/sheet_selector.html", {
        "request": request,
        "sheet_names": sheet_names,
        "saved_path": saved_path,
    })


@app.post("/sheet-info", response_class=HTMLResponse)
async def sheet_info(
    request: Request,
    sheet_name: str = Form(...),
    saved_path: str = Form(...),
):
    df = pd.read_excel(saved_path, sheet_name=sheet_name)
    columns = df.columns.tolist()
    row_count = len(df)

    return templates.TemplateResponse("partials/sheet_info.html", {
        "request": request,
        "sheet_name": sheet_name,
        "columns": columns,
        "row_count": row_count,
    })
