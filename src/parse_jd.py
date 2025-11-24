"""
Rule-based Job Description Parser
"""

import re
from typing import Dict, Any, List

def clean_text(text: str) -> str:
    text = text.replace("\t", " ")
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_sections(text: str) -> Dict[str, str]:
    """
    Extract common JD sections using headings:
    Responsibilities, Requirements, Nice-to-have, Skills
    """
    SECTION_HEADERS = [
        "responsibilities", "requirements", "must-haves", "nice-to-have",
        "skills", "work environment", "company overview", "summary"
    ]
    sections = {}
    for header in SECTION_HEADERS:
        regex = re.compile(rf"(?i){header}[:\n]", re.MULTILINE)
        match = regex.search(text)
        if match:
            start = match.end()
            next_starts = [
                m.start() + start
                for h in SECTION_HEADERS if (m := re.search(rf"(?i){h}[:\n]", text[start:]))
            ]
            end = min(next_starts) if next_starts else len(text)
            sections[header] = text[start:end].strip()
    return sections


def extract_skills(sections: Dict[str, str]) -> List[str]:
    """
    Combine skills from 'skills', 'requirements', 'must-haves', 'nice-to-have'
    """
    skills_text = []
    for key in ["skills", "requirements", "must-haves", "nice-to-have"]:
        if key in sections:
            skills_text.append(sections[key])
    # Split on common separators
    raw_skills = re.split(r"[,;\n-]", " ".join(skills_text))
    return [s.strip().lower() for s in raw_skills if s.strip()]


def parse_jd(text: str) -> Dict[str, Any]:
    text = clean_text(text)
    sections = extract_sections(text)

    parsed = {
        "position": "",
        "company": "",
        "location": "",
        "summary": sections.get("summary", ""),
        "responsibilities": re.split(r"[\n-]", sections.get("responsibilities", "")),
        "requirements": re.split(r"[\n-]", sections.get("requirements", "")),
        "nice_to_have": re.split(r"[\n-]", sections.get("nice-to-have", "")),
        "skills": extract_skills(sections),
        "sections": sections
    }

    # Clean empty strings
    for key in ["responsibilities", "requirements", "nice_to_have"]:
        parsed[key] = [s.strip() for s in parsed[key] if s.strip()]

    return parsed
