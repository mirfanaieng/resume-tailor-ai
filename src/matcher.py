# matcher.py
import os
import json
import logging
from typing import List, Dict, Any
from keybert import KeyBERT
import spacy

# Import your previous modules
import extractor
import parser

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()

def extract_keywords(text: str, n: int = 15) -> List[str]:
    if not text or not text.strip():
        return []
    keywords = kw_model.extract_keywords(
        text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=n
    )
    return [kw[0].lower() for kw in keywords]

def clean_skills(skills: List[str]) -> List[str]:
    return list({s.lower().strip() for s in skills if s.strip()})

def match_skills(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, Any]:
    resume_set = set(clean_skills(resume_skills))
    jd_set = set(clean_skills(jd_skills))

    matched = list(resume_set & jd_set)
    missing = list(jd_set - resume_set)

    match_score = round((len(matched) / len(jd_set)) * 100, 2) if jd_set else 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": match_score
    }

def save_report(report: Dict[str, Any], filename: str = "data/skill_match_report.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(report, f, indent=4)
    logging.info(f"Report saved to {filename}")

if __name__ == "__main__":
    # 1. Extract raw text using your extractor
    resume_text = extractor.extract_text_from_file("data/cv.pdf")
    jd_text = extractor.extract_text_from_file("data/jd.txt")

    # 2. Parse structured data using your parser
    parsed_resume = parser.parse_document(resume_text, doc_type="resume", file_name="data/cv.pdf")  # returns dict with 'skills', 'experience', etc.
    parsed_jd = parser.parse_document(jd_text, doc_type="jd", file_name="data/jd.txt")            # returns dict with 'skills', 'requirements', etc.

    # 3. Use skills for matching
    resume_skills = parsed_resume.get("skills", [])
    jd_skills = parsed_jd.get("skills", [])

    # Optional: fallback to KeyBERT if parser didn't detect enough skills
    if not resume_skills:
        resume_skills = extract_keywords(resume_text)
    if not jd_skills:
        jd_skills = extract_keywords(jd_text)

    # 4. Match skills
    report = match_skills(resume_skills, jd_skills)

    # 5. Save report
    save_report(report)
    logging.info(json.dumps(report, indent=4))
