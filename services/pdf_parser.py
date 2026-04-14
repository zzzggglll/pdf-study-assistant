from typing import List

from pypdf import PdfReader


def extract_text(path: str, max_pages: int = 30) -> str:
    """
    Extract plain text from a PDF file.
    max_pages keeps processing bounded for performance and token budget.
    """
    reader = PdfReader(path)
    parts: List[str] = []
    for idx, page in enumerate(reader.pages):
        if idx >= max_pages:
            break
        # pypdf may return None when a page has no extractable text.
        text = page.extract_text() or ""
        clean = text.strip()
        if clean:
            parts.append(clean)
    return "\n\n".join(parts)
