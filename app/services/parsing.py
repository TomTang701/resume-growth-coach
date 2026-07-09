from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile


SUPPORTED_EXTENSIONS = {".txt", ".pdf"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_DOCUMENT_CHARS = 1_000_000


async def extract_input_text(text: str | None, file: UploadFile | None) -> tuple[str, str, str | None]:
    if text and text.strip():
        if len(text) > MAX_DOCUMENT_CHARS:
            raise HTTPException(status_code=413, detail="Pasted document is too large for the local MVP.")
        return normalize_text(text), "text", None

    if file is None or not file.filename:
        raise HTTPException(status_code=400, detail="Provide text content or upload a .txt or .pdf file.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .txt and .pdf uploads are supported.")

    content = await read_limited(file, MAX_UPLOAD_BYTES)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Uploaded file is too large for the local MVP.")

    if suffix == ".txt":
        extracted = decode_text(content)
    else:
        extracted = extract_pdf_text(content)

    if not extracted.strip():
        raise HTTPException(status_code=400, detail="The document is empty or could not be parsed.")

    return normalize_text(extracted), suffix.lstrip("."), file.filename


async def read_limited(file: UploadFile, limit: int, chunk_size: int = 64 * 1024) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while total <= limit:
        chunk = await file.read(min(chunk_size, limit + 1 - total))
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > limit:
            break
    return b"".join(chunks)


def decode_text(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def extract_pdf_text(content: bytes) -> str:
    try:
        import pdfplumber
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="PDF parsing dependency is not installed.") from exc

    pages: list[str] = []
    try:
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="The PDF could not be parsed.") from exc
    return "\n".join(pages)


def normalize_text(value: str) -> str:
    lines = [line.strip() for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    compact_lines: list[str] = []
    previous_blank = False
    for line in lines:
        is_blank = not line
        if is_blank and previous_blank:
            continue
        compact_lines.append(line)
        previous_blank = is_blank
    return "\n".join(compact_lines).strip()


def preview_text(value: str, limit: int = 320) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def detect_resume_sections(text: str) -> list[str]:
    headings = {
        "education": ("education", "academic"),
        "experience": ("experience", "employment", "work history"),
        "projects": ("projects", "project"),
        "skills": ("skills", "technical skills", "technologies"),
        "certifications": ("certifications", "certificates"),
    }
    lower = text.lower()
    return [label for label, variants in headings.items() if any(token in lower for token in variants)]
