# src/matcher.py
import logging
from typing import List, Dict, Any
from extractor import extract_text_from_file
from parser import parse_document

# Optional: keep KeyBERT as smart fallback only
try:
    from keybert import KeyBERT
    kw_model = KeyBERT()
    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("matcher")


def extract_keywords_fallback(text: str, top_n: int = 12) -> List[str]:
    """Fallback using KeyBERT only if installed"""
    if not KEYBERT_AVAILABLE or not text:
        return []
    try:
        keywords = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words="english",
            top_n=top_n,
            use_mmr=True,
            diversity=0.5
        )
        return [kw[0].lower() for kw in keywords]
    except:
        return []


def match_skills(
    resume_skills: List[str],
    jd_skills: List[str],
    resume_text: str = "",
    jd_text: str = ""
) -> Dict[str, Any]:
    """
    Main skill matching function.
    Uses parser skills first → falls back to KeyBERT only if needed.
    """
    # Clean and normalize
    def clean(skill_list):
        return {str(s).strip().lower() for s in skill_list if s and str(s).strip()}

    resume_set = clean(resume_skills)
    jd_set = clean(jd_skills)

    # Fallback: if parser gave us almost nothing, use KeyBERT
    if len(resume_set) < 3 and resume_text:
        logger.info("Parser gave few resume skills → using KeyBERT fallback")
        resume_set.update(clean(extract_keywords_fallback(resume_text)))

    if len(jd_set) < 3 and jd_text:
        logger.info("Parser gave few JD skills → using KeyBERT fallback")
        jd_set.update(clean(extract_keywords_fallback(jd_text)))

    if not jd_set:
        return {
            "match_score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "total_required": 0,
            "message": "No skills detected in Job Description"
        }

    matched = sorted(list(resume_set & jd_set))
    missing = sorted(list(jd_set - resume_set))

    match_score = round((len(matched) / len(jd_set)) * 100, 1)

    logger.info(f"Skill Match: {len(matched)}/{len(jd_set)} → {match_score}%")

    return {
        "match_score": match_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "total_required": len(jd_set),
        "matched_count": len(matched),
        "source": "parser + keybert_fallback" if (len(resume_set) > len(clean(resume_skills)) or len(jd_set) > len(clean(jd_skills))) else "parser_only"
    }


# High-level function used by Gradio / main pipeline
def get_match_report(
    parsed_resume: Dict[str, Any],
    parsed_jd: Dict[str, Any],
    resume_text: str = "",
    jd_text: str = ""
) -> Dict[str, Any]:
    resume_skills = parsed_resume.get("skills", [])
    jd_skills = parsed_jd.get("skills", [])

    return match_skills(resume_skills, jd_skills, resume_text, jd_text)


# Test it
if __name__ == "__main__":
    

    resume_path = "data/cv.pdf"
    jd_path = "data/jd.txt"

    resume_text = extract_text_from_file(resume_path)
    jd_text = extract_text_from_file(jd_path)

    parsed_resume = parse_document(resume_text, "resume")
    parsed_jd = parse_document(jd_text, "jd")

    report = get_match_report(parsed_resume, parsed_jd, resume_text, jd_text)
    print("\nMATCH REPORT:")
    print(f"Score: {report['match_score']}%")
    print(f"Matched: {', '.join(report['matched_skills'])}")
    print(f"Missing: {', '.join(report['missing_skills'][:10])}")