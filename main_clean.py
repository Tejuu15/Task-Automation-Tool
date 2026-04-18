# Task Automation Toolkit – FastAPI Web Dashboard
# Automates common tasks: file cleanup, PDF merge, CSV to Excel
# Run: python main.py

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os, shutil, csv
from pathlib import Path
from PyPDF2 import PdfMerger
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BASE_DIR = Path("automation")
BASE_DIR.mkdir(exist_ok=True)

# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/cleanup", response_class=HTMLResponse)
def cleanup(request: Request, ext: str = Form(...)):
    target = BASE_DIR / ext
    target.mkdir(exist_ok=True)
    moved = 0
    for f in BASE_DIR.iterdir():
        if f.is_file() and f.suffix == f'.{ext}':
            shutil.move(str(f), target / f.name)
            moved += 1
    return templates.TemplateResponse("index.html", {
        "request": request,
        "msg": f"Moved {moved} .{ext} files"
    })

@app.post("/merge-pdf", response_class=HTMLResponse)
def merge_pdf(request: Request, files: list[UploadFile] = File(...)):
    merger = PdfMerger()
    for f in files:
        merger.append(f.file)
    out = BASE_DIR / "merged.pdf"
    merger.write(out)
    merger.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "msg": "PDFs merged successfully → merged.pdf"
    })

@app.post("/csv-excel", response_class=HTMLResponse)
def csv_to_excel(request: Request, file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    out = BASE_DIR / "output.xlsx"
    df.to_excel(out, index=False)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "msg": "CSV converted to Excel → output.xlsx"
    })

# ---------- Run ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
