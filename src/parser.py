import re
import json
import spacy
import sys
from pathlib import Path

# Load spaCy model (English)
nlp = spacy.load("en_core_web_sm")

def clean_text(text: str) -> str:
    """Basic cleanup — removes multiple spaces and line breaks"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_email(text: str):
    """Find first email in text"""
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None


def extract_sections(text: str):
    """
    Identify resume sections dynamically.
    Finds each section header and captures content until next header.
    """
    sections = {}
    headers = [
        "summary",
        "objective",
        "skills",
        "experience",
        "work history",
        "employment",
        "education",
        "projects",
        "certifications",
        "achievements",
    ]

    # Build regex for all section headers
    pattern = r"(?i)({})".format("|".join(headers))
    matches = list(re.finditer(pattern, text))

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        key = match.group(0).lower()
        sections[key] = text[start:end].strip()

    return sections


def parse_resume(text: str, file_name: str = None):
    """Parse resume text into structured fields"""
    text = clean_text(text)
    doc = nlp(text)

    # Extract name (fallback to filename if not found)
    names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    name = names[0] if names else Path(file_name).stem if file_name else None

    parsed = {
        "name": name,
        "email": extract_email(text),
        "sections": extract_sections(text),
    }
    return parsed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/parser.py <resume_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    filename = (file_path.split('/')[-1]).split('.')[0]
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    parsed = parse_resume(text, file_path)

    # Save JSON output

    output_file = Path("data", f"{filename}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Parsed data saved to {output_file.resolve()}")
    print(json.dumps(parsed, indent=2))
