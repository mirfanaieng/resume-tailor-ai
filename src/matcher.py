import spacy
from keybert import KeyBERT
import json


nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()


def extract_keywords(text, n=15):
    """Extracts top keywords using KeyBERT"""
    keywords = kw_model.extract_keywords(
        text, 
        keyphrase_ngram_range=(1, 2), 
        stop_words='english', 
        top_n=n
    )
    return [kw[0].lower() for kw in keywords]

def clean_skills(skills):
    """Normalize skill names"""
    return list(set([s.lower().strip() for s in skills]))

def match_skills(resume_text, jd_text):
    resume_skills = clean_skills(extract_keywords(resume_text))
    jd_skills = clean_skills(extract_keywords(jd_text))

    matched = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    match_score = round((len(matched) / len(jd_skills)) * 100, 2) if jd_skills else 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": match_score
    }

def save_report(report, filename="data/skill_match_report.json"):
    with open(filename, "w") as f:
        json.dump(report, f, indent=4)

if __name__ == "__main__":
    with open("data/resume_sample.txt", "r") as f:
        resume_text = f.read()
    with open("data/jd_sample.txt", "r") as f:
        jd_text = f.read()

    report = match_skills(resume_text, jd_text)
    save_report(report)
    print(json.dumps(report, indent=4))
