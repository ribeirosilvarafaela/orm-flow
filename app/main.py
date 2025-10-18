from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pathlib import Path
import uuid
from .pdf_to_img import pdf_to_images
from .omr import run_audiveris_on_images
from .parse_musicxml import extract_notes_to_txt
from .settings import settings

app = FastAPI(title="OMR Notes Extractor")

@app.get("/", response_class=HTMLResponse)
def index():
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)

@app.post("/extract")
async def extract_notes(pdf: UploadFile = File(...)):
    run_id = uuid.uuid4().hex[:8]
    work_dir = Path(settings.OUTPUT_DIR) / run_id
    work_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = work_dir / pdf.filename
    pdf_path.write_bytes(await pdf.read())

    imgs_dir = work_dir / "pages"
    pdf_to_images(pdf_path, imgs_dir)

    xml_dir = work_dir / "xml"
    musicxml_path = run_audiveris_on_images(imgs_dir, xml_dir)

    lines = extract_notes_to_txt(musicxml_path)
    txt_path = work_dir / "notes.txt"
    txt_path.write_text("\n".join(lines), encoding="utf-8")

    return {"txt_path": str(txt_path), "musicxml_path": str(musicxml_path), "run_id": run_id}

@app.get("/download")
def download(path: str):
    p = Path(path)
    if not p.exists():
        return JSONResponse({"error": "Arquivo não encontrado"}, status_code=404)
    return FileResponse(p)
