"""FastAPI server for template filling."""

from __future__ import annotations

import io
import os
import tempfile
import zipfile
from typing import TYPE_CHECKING

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from template_filler.data_loading import read_data_file
from template_filler.word_filler import fill_template

if TYPE_CHECKING:
    from collections.abc import Iterator

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/fill-templates")
async def fill_templates(
    data_file: UploadFile,
    template_file: UploadFile,
) -> StreamingResponse:
    """Process data file and template, return zip of filled documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded files
        data_path = os.path.join(temp_dir, data_file.filename or "data.xlsx")
        template_path = os.path.join(temp_dir, template_file.filename or "template.docx")

        with open(data_path, "wb") as f:
            f.write(await data_file.read())
        with open(template_path, "wb") as f:
            f.write(await template_file.read())

        # Process files and create zip
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            data_rows: Iterator[dict[str, str]] = read_data_file(data_path)
            for idx, row_data in enumerate(data_rows, start=1):
                output_path = os.path.join(temp_dir, f"filled_document_{idx}.docx")
                fill_template(template_path, output_path, row_data)
                zip_file.write(output_path, f"filled_document_{idx}.docx")

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=filled_documents.zip"},
        )


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
