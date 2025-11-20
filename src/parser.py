"""
Robust resume parser for Resume Tailor / JD Matcher.
"""

import re
import json
from pathlib import Path
from extractor import extract_text_from_file


try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


# -------------------------
# TEXT CLEANING
# -------------------------

def clean_text(text: str) -> str:
    """
    Lightweight cleanup: preserve line breaks, remove extra spaces.
    """
    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove duplicate spaces
    text = re.sub(r" {2,}", " ", text)

    # Normalize multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# -------------------------
# EMAIL & PHONE EXTRACTION
# -------------------------

def extract_email(text: str):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str):
    # Covers formats: +92 300 1234567, 0300-1234567, (0300) 1234567
    pattern = r"(\+?\d{1,3}[- ]?)?\(?\d{2,4}\)?[- ]?\d{6,8}"
    match = re.search(pattern, text)
    return match.group(0) if match else None


# -------------------------
# SECTION EXTRACTION (STRONG)
# -------------------------

SECTION_HEADERS = [
    "summary", "about me", "objective",
    "skills", "technical skills",
    "experience", "work experience",
    "employment history",
    "projects", "project experience",
    "education", "academics",
    "certifications",
    "achievements",
]


def extract_sections(text: str):
    """
    Stronger section extractor:
    - matches uppercase
    - matches 'Skills:' or 'EXPERIENCE -'
    - captures until next section header
    """
    sections = {}

    # Build flexible regex for headers
    header_regex = r"(?im)^({})(?=\s*[:\-]?\s*$)".format("|".join([re.escape(h) for h in SECTION_HEADERS]))

    matches = list(re.finditer(header_regex, text))

    for i, match in enumerate(matches):
        section_title = match.group(1).lower()

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        content = text[start:end].strip()
        sections[section_title] = content

    return sections


# -------------------------
# NAME EXTRACTOR (IMPROVED)
# -------------------------


SKIP_KEYWORDS = {
    "email", "phone", "@", "linkedin", "github", "www", "http",
    "engineer", "developer", "manager", "specialist", "lead", "senior",
    "dashboard", "company", "department", "project", "experience",
    "summary", "profile", "objective", "resume", "curriculum", "vitae"
}

def extract_name(text: str, file_name: str = None) -> str | None:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return Path(file_name).stem if file_name else None

    # --- Priority 1: First non-empty line that looks like a real name ---
    for i, line in enumerate(lines[:10]):  # only check top 10 lines
        lowered = line.lower()

        # Skip obvious junk lines
        if any(k in lowered for k in SKIP_KEYWORDS):
            continue
        if re.search(r'\d{3,}|\b(cv|resume|curriculum)\b', lowered):
            continue

        # Strong name signals
        words = line.split()
        if 2 <= len(words) <= 4 and re.match(r"^[A-Za-z\s\.\-']+$", line):
            # Title case or ALL CAPS = very strong signal for name
            if line.istitle() or line.isupper():
                # Bonus: if it's the very first line → almost certainly the name
                if i == 0:
                    return line.strip()
                return line.strip()

    # --- Priority 2: Any title-case / uppercase 2–4 word line in top 10 ---
    for line in lines[:10]:
        words = line.split()
        lowered = line.lower()
        if (2 <= len(words) <= 4 and
            re.match(r"^[A-Za-z\s\.\-']+$", line) and
            not any(k in lowered for k in SKIP_KEYWORDS) and
            (line.istitle() or line.isupper())):
            return line.strip()

    # --- Priority 3: Fallback to first valid-looking line ---
    for line in lines[:5]:
        words = line.split()
        if 2 <= len(words) <= 4 and re.match(r"^[A-Za-z\s\.\-']+$", line):
            return line.strip()

    # --- Final fallback: filename ---
    if file_name:
        name = Path(file_name).stem
        # Clean common prefixes/suffixes
        name = re.sub(r'^(cv|resume|cv_|-|_)+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'(\s+resume|\s+cv).*', '', name, flags=re.IGNORECASE)
        return name.strip() or None

    return None



# -------------------------
# MAIN PARSER FUNCTION
# -------------------------

def parse_resume(text: str, file_name: str = None):
    text = clean_text(text)

    parsed = {
        "name": extract_name(text, file_name),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "sections": extract_sections(text),
    }

    return parsed


# -------------------------
# CLI FOR LOCAL TESTING
# -------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parser.py <resume text file>")
        sys.exit(1)

    file_path = sys.argv[1]
    filename = Path(file_path).stem

    text = extract_text_from_file(file_path)
    print("extracted text: ",text[:50])


    parsed = parse_resume(text, file_path)

    # Ensure output folder exists
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"{filename}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Parsed data saved to {output_file.resolve()}")
    print(json.dumps(parsed, indent=2))
