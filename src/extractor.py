"""
Robust text extractor for resumes and job descriptions.
Supports: .txt, .md, .docx, .pdf
"""

from pathlib import Path
import re
import logging
import pdfplumber

try:
    import docx2txt
except ImportError:
    docx2txt = None

logger = logging.getLogger("extractor")
logging.basicConfig(level=logging.INFO)


# -------------------------
# NORMALIZATION
# -------------------------
def normalize_text_block(text: str) -> str:
    """
    Clean text:
    - Preserve line breaks
    - Remove trailing spaces
    - Remove multiple blank lines
    - Fix spacing
    """
    text = text.replace("\r", "")
    # Remove trailing spaces on each line
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    # Remove multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove extra spaces
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def normalize_whitespace(text: str) -> str:
    # backward compatible wrapper
    return normalize_text_block(text)


# -------------------------
# DOCX EXTRACTOR
# -------------------------
def extract_text_from_docx(path: str) -> str:
    if docx2txt is None:
        raise RuntimeError("docx2txt not installed. Run: pip install docx2txt")
    try:
        text = docx2txt.process(path) or ""
        return normalize_text_block(text)
    except Exception as e:
        logger.error("DOCX extraction failed (%s): %s", path, e)
        return ""


# -------------------------
# PDF EXTRACTOR (PLUMBER - industry reliable)
# -------------------------
def extract_text_from_pdf(path: str) -> str:
    try:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if page_text:
                    text += page_text + "\n\n"
        return normalize_text_block(text)
    except Exception as e:
        logger.error("PDF extraction failed (%s): %s", path, e)
        return ""


# -------------------------
# TXT / MD EXTRACTOR
# -------------------------
def extract_text_from_txt(path: str) -> str:
    try:
        return normalize_text_block(Path(path).read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        logger.error("TXT read failed (%s): %s", path, e)
        return ""


# -------------------------
# MAIN FILE EXTRACTOR
# -------------------------
SUPPORTED = {".txt", ".md", ".docx", ".pdf"}


def extract_text_from_file(path: str) -> str:
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = p.suffix.lower()

    if suffix not in SUPPORTED:
        logger.error("Unsupported file type: %s", suffix)
        return ""

    if suffix in [".txt", ".md"]:
        return extract_text_from_txt(path)
    if suffix == ".docx":
        return extract_text_from_docx(path)
    if suffix == ".pdf":
        return extract_text_from_pdf(path)

    return ""  # fallback


# -------------------------
# QUICK PREVIEW
# -------------------------
def quick_preview(text: str, max_chars: int = 800) -> str:
    if not text:
        return "(no text extracted)"
    text = text.strip()
    return text[:max_chars] + ("\n...[truncated]" if len(text) > max_chars else "")


# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to resume or JD file")
    parser.add_argument("--save", action="store_true", help="Save full extracted text to extracted_output.txt")
    args = parser.parse_args()

    path = args.file
    print(f"\n📄 Extracting text from: {path}")

    text = extract_text_from_file(path)

    print("\n=== Extracted Text Preview (first 800 chars) ===\n")
    preview = text[:800] + ("\n...[truncated]" if len(text) > 800 else "")
    print(preview)

    print("\n=== Extraction Stats ===")
    print("Characters:", len(text))
    print("Words:", len(text.split()))

    # Optional save extracted txt
    if args.save:
        output_dir = Path("data")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "extracted_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n💾 Full extracted text saved to {output_file.resolve()}")
