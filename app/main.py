from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

from .annotate import annotate_score
from .harmonize import Harmonizer
from .pdf_to_img import pdf_to_images
from .settings import settings

app = FastAPI(title="Anotador de Acordes para Partituras")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.post("/api/process")
async def process_pdf(pdf: UploadFile = File(...)):
    if not pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")

    run_id = uuid.uuid4().hex[:8]
    work_dir = Path(settings.OUTPUT_DIR) / run_id
    work_dir.mkdir(parents=True, exist_ok=True)

    original_pdf_path = work_dir / "partitura.pdf"
    original_pdf_path.write_bytes(await pdf.read())

    pages_dir = work_dir / "paginas"
    page_images = pdf_to_images(original_pdf_path, pages_dir)
    if not page_images:
        raise HTTPException(status_code=400, detail="Não foi possível converter o PDF em imagens.")

    harmonizer = Harmonizer()
    annotated_pages: list[Path] = []
    resumo: list[dict[str, object]] = []

    for idx, image_path in enumerate(page_images, start=1):
        chords = harmonizer.infer_chords_from_image(image_path)
        out_img = work_dir / "anotadas" / f"page_{idx:03d}.png"
        annotate_score(image_path, chords, out_img)
        annotated_pages.append(out_img)
        resumo.append({"pagina": idx, "acordes": chords})

    output_pdf = work_dir / "partitura_com_acordes.pdf"
    first_image = Image.open(annotated_pages[0]).convert("RGB")
    remaining = [Image.open(p).convert("RGB") for p in annotated_pages[1:]]
    first_image.save(output_pdf, save_all=True, append_images=remaining, format="PDF")

    return {
        "run_id": run_id,
        "download_url": f"/download/{run_id}",
        "resumo": resumo,
    }


@app.get("/download/{run_id}")
def download(run_id: str):
    pdf_path = Path(settings.OUTPUT_DIR) / run_id / "partitura_com_acordes.pdf"
    if not pdf_path.exists():
        return JSONResponse({"erro": "Arquivo não encontrado"}, status_code=404)
    return FileResponse(pdf_path, filename=pdf_path.name, media_type="application/pdf")
