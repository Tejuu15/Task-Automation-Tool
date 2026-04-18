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


# -----------------------------
# Create folder: templates/
# Create file: templates/index.html
# -----------------------------

"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Automation Toolkit</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap" rel="stylesheet">
<style>
body {
  font-family: Inter, sans-serif;
  background: linear-gradient(135deg, #020617, #000);
  color: #e5e7eb;
  margin: 0;
  padding: 40px;
}
.container { max-width: 900px; margin: auto; }
h1 { font-size: 2.5rem; margin-bottom: 20px; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}
.card {
  background: rgba(2,6,23,.9);
  border-radius: 18px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0,0,0,.7);
}
h3 { margin-top: 0; }
form { display: flex; gap: 10px; flex-wrap: wrap; }
input, button {
  padding: 12px;
  border-radius: 10px;
  border: none;
  font-size: 14px;
}
input {
  flex: 1;
  background: #020617;
  border: 1px solid #1e293b;
  color: white;
}
button {
  background: #a78bfa;
  color: #020617;
  font-weight: 700;
  cursor: pointer;
}
button:hover { background: #8b5cf6; }
.alert {
  margin-bottom: 20px;
  padding: 14px;
  background: #022c22;
  border-radius: 12px;
  color: #4ade80;
}
</style>
</head>
<body>
<div class="container">
<h1>⚙️ Task Automation Toolkit</h1>

{% if msg %}
<div class="alert">{{ msg }}</div>
{% endif %}

<div class="grid">

<div class="card">
<h3>📁 File Cleanup</h3>
<form method="post" action="/cleanup">
  <input name="ext" placeholder="Extension (e.g. pdf)" required>
  <button>Clean</button>
</form>
</div>

<div class="card">
<h3>📄 Merge PDFs</h3>
<form method="post" action="/merge-pdf" enctype="multipart/form-data">
  <input type="file" name="files" multiple required>
  <button>Merge</button>
</form>
</div>

<div class="card">
<h3>📊 CSV → Excel</h3>
<form method="post" action="/csv-excel" enctype="multipart/form-data">
  <input type="file" name="file" required>
  <button>Convert</button>
</form>
</div>

</div>
</div>
</body>
</html>
"""
