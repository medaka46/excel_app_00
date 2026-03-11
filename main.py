import os
import uuid
import json
import pandas as pd
from datetime import date, datetime
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_XLSX = os.path.join(BASE_DIR, "Sample-Project-data-2025-end-004.xlsx")


def _safe_excel_path(path: str) -> str:
    """
    Allow reading Excel files only from:
    - this app directory (for bundled sample files)
    - uploads directory (for user uploads)
    """
    if not path:
        raise HTTPException(status_code=400, detail="Missing path")

    abs_path = os.path.abspath(path)
    allowed_roots = [
        os.path.abspath(BASE_DIR),
        os.path.abspath(os.path.join(BASE_DIR, UPLOAD_DIR)),
    ]
    if not any(abs_path == r or abs_path.startswith(r + os.sep) for r in allowed_roots):
        raise HTTPException(status_code=400, detail="Path is not allowed")
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="Excel file not found")
    if not abs_path.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx/.xls files are supported")
    return abs_path


def _json_safe(value):
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    # pandas Timestamp inherits datetime, but keep explicit for clarity
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def _df_to_json_rows(df: pd.DataFrame) -> list[dict]:
    # Convert pandas missing values (NaN/pd.NA) to None (valid JSON null)
    df_obj = df.astype(object).where(pd.notna(df), None)
    rows = df_obj.to_dict(orient="records")
    # Ensure datetime-like values are JSON-friendly strings
    return [{k: _json_safe(v) for k, v in row.items()} for row in rows]


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
    xf = pd.ExcelFile(_safe_excel_path(saved_path))
    sheet_names = xf.sheet_names

    return templates.TemplateResponse("partials/sheet_selector.html", {
        "request": request,
        "sheet_names": sheet_names,
        "saved_path": _safe_excel_path(saved_path),
    })


@app.get("/load-sample", response_class=HTMLResponse)
async def load_sample(request: Request):
    saved_path = _safe_excel_path(SAMPLE_XLSX)
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
    df = pd.read_excel(_safe_excel_path(saved_path), sheet_name=sheet_name)
    columns = df.columns.tolist()
    row_count = len(df)
    unique_vals = {
        col: sorted(df[col].dropna().astype(str).unique().tolist())
        for col in columns
        if df[col].dropna().astype(str).nunique() <= 10
    }

    return templates.TemplateResponse("partials/sheet_info.html", {
        "request": request,
        "saved_path": _safe_excel_path(saved_path),
        "sheet_name": sheet_name,
        "columns": columns,
        "row_count": row_count,
        "unique_vals": unique_vals,
    })


def _apply_filters(df, active_filters):
    for f in active_filters:
        col_data = df[f["col"]]
        val = f["val"]
        op = f["op"]
        if op == "=":
            df = df[col_data.astype(str) == val]
        elif op == "!=":
            df = df[col_data.astype(str) != val]
        elif op == "contains":
            df = df[col_data.astype(str).str.contains(val, case=False, na=False)]
        elif op == ">":
            df = df[pd.to_numeric(col_data, errors="coerce") > float(val)]
        elif op == ">=":
            df = df[pd.to_numeric(col_data, errors="coerce") >= float(val)]
        elif op == "<":
            df = df[pd.to_numeric(col_data, errors="coerce") < float(val)]
        elif op == "<=":
            df = df[pd.to_numeric(col_data, errors="coerce") <= float(val)]
    return df


def _filter_response(request, saved_path, sheet_name, active_filters, templates):
    df = pd.read_excel(_safe_excel_path(saved_path), sheet_name=sheet_name)
    all_columns = df.columns.tolist()
    unique_vals = {
        c: sorted(df[c].dropna().astype(str).unique().tolist())
        for c in all_columns
        if df[c].dropna().astype(str).nunique() <= 10
    }
    df = _apply_filters(df, active_filters)
    return templates.TemplateResponse("partials/filter_results.html", {
        "request": request,
        "saved_path": _safe_excel_path(saved_path),
        "sheet_name": sheet_name,
        "columns": all_columns,
        "active_filters": active_filters,
        "filters_json": json.dumps(active_filters),
        "unique_vals": unique_vals,
        "rows": _df_to_json_rows(df),
        "row_count": len(df),
    })


@app.get("/clear-filters", response_class=HTMLResponse)
async def clear_filters():
    return ""


@app.post("/filter", response_class=HTMLResponse)
async def filter_rows(
    request: Request,
    saved_path: str = Form(...),
    sheet_name: str = Form(...),
    filters: str = Form("[]"),
    col: str = Form(...),
    operator: str = Form(...),
    value: str = Form(...),
):
    active_filters = json.loads(filters)
    active_filters.append({"col": col, "op": operator, "val": value})
    return _filter_response(request, saved_path, sheet_name, active_filters, templates)


@app.post("/remove-filter", response_class=HTMLResponse)
async def remove_filter(
    request: Request,
    saved_path: str = Form(...),
    sheet_name: str = Form(...),
    filters: str = Form("[]"),
    index: int = Form(...),
):
    active_filters = json.loads(filters)
    if 0 <= index < len(active_filters):
        active_filters.pop(index)
    if not active_filters:
        return HTMLResponse("")
    return _filter_response(request, saved_path, sheet_name, active_filters, templates)


@app.get("/api/sample/sheets", response_class=JSONResponse)
async def api_sample_sheets():
    saved_path = _safe_excel_path(SAMPLE_XLSX)
    xf = pd.ExcelFile(saved_path)
    return {"file": os.path.basename(saved_path), "path": saved_path, "sheets": xf.sheet_names}


@app.get("/api/sample/sheet", response_class=JSONResponse)
async def api_sample_sheet(
    sheet_name: str = Query(...),
    limit: int = Query(200, ge=1, le=5000),
):
    saved_path = _safe_excel_path(SAMPLE_XLSX)
    df = pd.read_excel(saved_path, sheet_name=sheet_name)
    df = df.head(limit)
    return {
        "file": os.path.basename(saved_path),
        "sheet": sheet_name,
        "columns": df.columns.tolist(),
        "row_count": int(len(df)),
        "rows": _df_to_json_rows(df),
    }
