"""
Rule-based Resume Parser
"""

import re
from pathlib import Path
from typing import Dict, Any, List

# -------------------------
# Helper functions
# -------------------------

def clean_text(text: str) -> str:
    """Remove extra spaces and normalize newlines"""
    text = text.replace("\t", " ")
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    pattern = r"(\+?\d{1,3}[- ]?)?\(?\d{2,4}\)?[- ]?\d{6,8}"
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def extract_sections(text: str) -> Dict[str, str]:
    """Basic section extraction using keywords"""
    SECTION_HEADERS = [
        "summary", "objective", "skills", "experience", "projects", "education", "certifications"
    ]
    sections = {}
    for header in SECTION_HEADERS:
        regex = re.compile(rf"(?i){header}[:\n]", re.MULTILINE)
        match = regex.search(text)
        if match:
            start = match.end()
            next_match = min(
                [m.start() for h in SECTION_HEADERS if (m := re.search(rf"(?i){h}[:\n]", text[start:]))],
                default=len(text[start:])
            )
            sections[header] = text[start:start+next_match].strip()
    return sections


def extract_name(text: str, file_name: str = None) -> str:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:10]:
        if 2 <= len(line.split()) <= 4 and re.match(r"^[A-Za-z\s\.\-']+$", line):
            return line.strip()
    return Path(file_name).stem if file_name else ""


# -------------------------
# Main parser
# -------------------------

def parse_resume(text: str, file_name: str = None) -> Dict[str, Any]:
    text = clean_text(text)
    parsed = {
        "name": extract_name(text, file_name),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "sections": extract_sections(text)
    }
    # Simple skill extraction
    skills_text = parsed["sections"].get("skills", "")
    parsed["skills"] = [s.strip().lower() for s in re.split(r"[,;\n]", skills_text) if s.strip()]
    return parsed
