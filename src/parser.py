"""
Unified Resume and JD Parser with Hybrid Rule-Based + LLM Fallback
"""

import re
import json
import logging
from pathlib import Path
from extractor import extract_text_from_file

# Optional NLP support if needed
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# LLM import
try:
    from ollama import Ollama
    llm_client = Ollama()
except Exception:
    llm_client = None
    logging.warning("Ollama client not available. LLM fallback won't work.")

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# -------------------------
# Text Cleaning
# -------------------------
def clean_text(text: str) -> str:
    text = text.replace("\t", " ")
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# -------------------------
# Email & Phone Extraction
# -------------------------
def extract_email(text: str):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

def extract_phone(text: str):
    pattern = r"(\+?\d{1,3}[- ]?)?\(?\d{2,4}\)?[- ]?\d{6,8}"
    match = re.search(pattern, text)
    return match.group(0) if match else None

# -------------------------
# Sections Extraction
# -------------------------
RESUME_HEADERS = [
    "summary", "about me", "objective",
    "skills", "technical skills",
    "experience", "work experience",
    "employment history",
    "projects", "project experience",
    "education", "academics",
    "certifications",
    "achievements",
]

JD_HEADERS = [
    "position", "job title", "role", "🧱", "must-haves", "nice-to-have", "what you'll do",
    "work environment", "culture", "communication", "career growth",
    "our approach", "contract details", "hiring process", "summary"
]

def extract_sections(text: str, headers=None):
    if headers is None:
        headers = RESUME_HEADERS
    sections = {}
    header_regex = r"(?im)^([^\w]*({}))[^\n]*".format("|".join([re.escape(h) for h in headers]))
    matches = list(re.finditer(header_regex, text))
    for i, match in enumerate(matches):
        section_title = match.group(2).lower()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        content = content.lstrip(": \n")
        sections[section_title] = content
    return sections

# -------------------------
# Name Extraction (Resume Only)
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
    for i, line in enumerate(lines[:10]):
        lowered = line.lower()
        if any(k in lowered for k in SKIP_KEYWORDS):
            continue
        if re.search(r'\d{3,}|\b(cv|resume|curriculum)\b', lowered):
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and re.match(r"^[A-Za-z\s\.\-']+$", line):
            if line.istitle() or line.isupper():
                if i == 0:
                    return line.strip()
                return line.strip()
    for line in lines[:5]:
        words = line.split()
        if 2 <= len(words) <= 4 and re.match(r"^[A-Za-z\s\.\-']+$", line):
            return line.strip()
    if file_name:
        name = Path(file_name).stem
        name = re.sub(r'^(cv|resume|cv_|-|_)+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'(\s+resume|\s+cv).*', '', name, flags=re.IGNORECASE)
        return name.strip() or None
    return None

# -------------------------
# Skills Extraction
# -------------------------
def extract_skills_from_section(section_text: str) -> list:
    if not section_text:
        return []
    section_text = section_text.lstrip(": \n").strip()
    split_phrases = ["Why", "If you are passionate", "Opportunity to work"]
    for phrase in split_phrases:
        section_text = section_text.split(phrase)[0]
    items = re.split(r"[\n,;•\-\u2022]", section_text)
    skills = [item.strip() for item in items if 1 <= len(item.strip().split()) <= 6]
    return skills

# -------------------------
# LLM Fallback
# -------------------------
def llm_extract_fields(text: str, doc_type: str = "jd") -> dict:
    if llm_client is None:
        logging.warning("LLM client not available, skipping fallback.")
        return {}
    prompt = f"""
    Extract key fields from this {doc_type} and return JSON with keys:
    For resume: name, email, phone, skills
    For jd: position, company, location, skills
    Text:
    {text}
    """
    try:
        result = llm_client.predict(model="phi:latest", prompt=prompt)
        # Expect result as JSON string
        return json.loads(result)
    except Exception as e:
        logging.warning(f"LLM extraction failed: {e}")
        return {}

# -------------------------
# Unified Parser
# -------------------------
def parse_document(text: str, doc_type: str = "resume", file_name: str = None) -> dict:
    text = clean_text(text)
    parsed = {}

    if doc_type == "resume":
        parsed = {
            "name": extract_name(text, file_name),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "sections": extract_sections(text, headers=RESUME_HEADERS),
        }
        skills_section = parsed["sections"].get("skills") or parsed["sections"].get("technical skills", "")
        parsed["skills"] = extract_skills_from_section(skills_section)
        # LLM fallback if skills empty
        if not parsed["skills"]:
            llm_data = llm_extract_fields(text, doc_type="resume")
            parsed.update(llm_data)

    elif doc_type == "jd":
        parsed = {
            "position": None,
            "location": None,
            "company": None,
            "sections": extract_sections(text, headers=JD_HEADERS),
        }
        sections = parsed["sections"]
        # Rule-based extraction
        pos_match = re.search(r'Position\s*[:\-]\s*(.+)', text, re.IGNORECASE)
        loc_match = re.search(r'(?:Work Mode|Location|Work Environment)\s*[:\-]\s*(.+)', text, re.IGNORECASE)
        parsed["position"] = pos_match.group(1).strip() if pos_match else None
        parsed["location"] = loc_match.group(1).strip() if loc_match else None
        parsed["company"] = sections.get("summary") or sections.get("our approach") or None

        skills_section = sections.get("must-haves") or sections.get("nice-to-have") or sections.get("what you'll do") or ""
        parsed["skills"] = extract_skills_from_section(skills_section)
        # LLM fallback if nothing found
        if not any([parsed["position"], parsed["company"], parsed["location"], parsed["skills"]]):
            llm_data = llm_extract_fields(text, doc_type="jd")
            parsed.update(llm_data)

    else:
        raise ValueError("doc_type must be 'resume' or 'jd'")

    return parsed

# -------------------------
# CLI Usage
# -------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python parser.py <file> <doc_type: resume/jd>")
        sys.exit(1)

    file_path = sys.argv[1]
    doc_type = sys.argv[2].lower()
    filename = Path(file_path).stem

    text = extract_text_from_file(file_path)
    parsed = parse_document(text, doc_type=doc_type, file_name=file_path)

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{filename}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)

    logging.info(f"✅ Parsed data saved to {output_file.resolve()}")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
