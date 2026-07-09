from pathlib import Path


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(file_path)
    if suffix == ".docx":
        return _extract_docx(file_path)
    raise ValueError(f"Unsupported resume file type: {suffix}")


def _extract_pdf(file_path: Path) -> str:
    try:
        import pdfplumber

        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            return text
    except Exception:
        pass

    from pypdf import PdfReader

    reader = PdfReader(str(file_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(file_path: Path) -> str:
    import docx

    document = docx.Document(str(file_path))
    return "\n".join(p.text for p in document.paragraphs)
