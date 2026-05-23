"""
Document Processor — Core Pipeline
Handles ingestion, text extraction, and cleaning for PDF/TXT files.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from PDF using pdfminer (fallback to PyPDF2)."""
    text = ""

    # Try pdfminer first (better accuracy)
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
        text = pdfminer_extract(filepath)
        if text and text.strip():
            return clean_text(text)
    except Exception as e:
        logger.warning(f"pdfminer failed for {filepath}: {e}")

    # Fallback: PyPDF2
    try:
        import PyPDF2
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        if text.strip():
            return clean_text(text)
    except Exception as e:
        logger.warning(f"PyPDF2 failed for {filepath}: {e}")

    logger.error(f"Could not extract text from {filepath}")
    return ""


def extract_text_from_txt(filepath: str) -> str:
    """Extract text from a plain text file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return clean_text(f.read())
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return ""


def clean_text(text: str) -> str:
    """Normalize whitespace and remove non-printable characters."""
    text = re.sub(r"[^\x20-\x7E\n\t]", " ", text)   # keep printable ASCII
    text = re.sub(r"[ \t]+", " ", text)               # collapse spaces
    text = re.sub(r"\n{3,}", "\n\n", text)             # collapse blank lines
    return text.strip()


def ingest_documents(folder: str) -> Dict[str, str]:
    """
    Read all PDF and TXT files from a folder.
    Returns a dict: {filename -> extracted_text}
    """
    folder_path = Path(folder)
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    docs: Dict[str, str] = {}
    supported = {".pdf", ".txt"}

    for file in sorted(folder_path.iterdir()):
        if file.suffix.lower() not in supported:
            continue

        logger.info(f"Processing: {file.name}")
        if file.suffix.lower() == ".pdf":
            text = extract_text_from_pdf(str(file))
        else:
            text = extract_text_from_txt(str(file))

        if text:
            docs[file.name] = text
        else:
            logger.warning(f"No text extracted from {file.name}")

    logger.info(f"Total documents ingested: {len(docs)}")
    return docs
