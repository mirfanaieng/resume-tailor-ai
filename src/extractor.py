"""
Text extractor for resumes and job descriptions.
Supports: .txt, .docx, .pdf
"""

from pathlib import Path
import re
import logging

try:
    import docx2txt
except:
    docx2txt = None

try:
    from pdfminer.high_level import extract_text as pdf_extract_text
except:
    pdf_extract_text = None

logger = logging.getLogger("extractor")
logging.basicConfig(level=logging.INFO)

def normalize_whitespace(text: str) -> str:
    return re.sub(r'\s+\n', '\n', re.sub(r'[ \t]+', ' ', text)).strip()

def extract_text_from_docx(path: str) -> str:
    if docx2txt is None:
        raise RuntimeError("docx2txt not installed.")
    try:
        text = docx2txt.process(path) or ""
        return normalize_whitespace(text)
    except Exception as e:
        logger.warning("docx extraction failed for %s: %s", path, e)
        return ""

def extract_text_from_pdf(path: str) -> str:
    if pdf_extract_text is None:
        raise RuntimeError("pdfminer.six not installed.")
    try:
        text = pdf_extract_text(path) or ""
        return normalize_whitespace(text)
    except Exception as e:
        logger.warning("pdf extraction failed for %s: %s", path, e)
        return ""

def extract_text_from_txt(path: str) -> str:
    try:
        return normalize_whitespace(Path(path).read_text(encoding='utf-8', errors='ignore'))
    except Exception as e:
        logger.warning("txt read failed for %s: %s", path, e)
        return ""

def extract_text_from_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    suffix = p.suffix.lower()
    if suffix in [".txt", ".md"]:
        return extract_text_from_txt(path)
    if suffix in [".docx", ".doc"]:
        return extract_text_from_docx(path)
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    try:
        return extract_text_from_txt(path)
    except Exception:
        logger.warning("Unsupported file type for %s", path)
        return ""

def quick_preview(text: str, max_chars: int = 800) -> str:
    if not text:
        return "(no text extracted)"
    text = text.strip()
    return text[:max_chars] + ("\n...[truncated]" if len(text) > max_chars else "")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to resume or JD file")
    args = parser.parse_args()
    txt = extract_text_from_file(args.file)
    print("=== Extracted preview ===")
    print(quick_preview(txt, max_chars=1000))
    print("\nWord count:", len([w for w in txt.split() if w.strip()]))
