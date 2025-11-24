# src/llm_tailor.py
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List
from groq import Groq
from dotenv import load_dotenv
import re

load_dotenv()
client = Groq()
logger = logging.getLogger("tailor")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def tailor_summary_and_skills(
    parsed_resume: Dict[str, Any],
    parsed_jd: Dict[str, Any],
    approved_keywords: List[str],
    output_dir: str = "output"
) -> Dict[str, Any]:
    """
    ETHICAL VERSION — Summary + Skills Only
    • NO company name in summary (your request)
    • Skills: only adds approved keywords (never removes)
    • Returns only the 2 updated sections
    """
    Path(output_dir).mkdir(exist_ok=True)
    approved_keywords = [k.strip().lower() for k in approved_keywords if k.strip()]

    # Original data
    original_skills = [s.strip().lower() for s in parsed_resume.get("skills", []) if s.strip()]
    name = parsed_resume.get("name", "Candidate").strip()
    job_title = parsed_jd.get("job_title", "Professional").strip()
    # ← Company name is NOT used anywhere in the summary

    prompt = f"""
You are a senior career coach writing a powerful, honest, and professional resume.

CANDIDATE: {name}
TARGET ROLE: {job_title}
CURRENT SKILLS: {", ".join(original_skills[:25])}
APPROVED KEYWORDS TO INCLUDE: {", ".join(approved_keywords) or "None"}

TASK: Return ONLY this exact JSON:

{{
  "summary": "3–4 line confident, targeted professional summary. 
  Use strong language. 
  Mention the target role naturally. 
  NEVER mention any company name.",
  "skills_to_add": ["Computer Vision", "Image Processing", "Large-scale Imagery"],
  "final_skills_list": ["Python", "PyTorch", "Computer Vision", ...],
  "justification": "Brief note"
}}

RULES:
- Summary must NOT contain any company name
- Only add skills from the approved_keywords list
- Never remove existing skills
- Return final_skills_list = original + approved (deduplicated, Title Case)
- Keep tone senior and confident

Return ONLY valid JSON.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800
        )
        raw = response.choices[0].message.content.strip()
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found")

        result = json.loads(json_match.group(0))

        # Final skills list: original + approved only
        final_skills = list(dict.fromkeys(
            [s.strip().title() for s in original_skills] +
            [s.strip().title() for s in result.get("skills_to_add", []) if s.strip().lower() in approved_keywords]
        ))

        result["final_skills_list"] = final_skills
        result["added_skills_count"] = len(final_skills) - len(original_skills)

        # Save clean output (NO company name anywhere)
        txt_path = Path(output_dir) / "SUMMARY_AND_SKILLS.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"{name}\n")
            f.write(f"{job_title}\n\n")
            f.write("PROFESSIONAL SUMMARY\n")
            f.write(result["summary"] + "\n\n")
            f.write("SKILLS\n")
            f.write(" • ".join(final_skills))

        result["updated_file"] = str(txt_path)
        logger.info(f"Summary & Skills updated (no company name) → {txt_path}")
        return result

    except Exception as e:
        logger.error(f"Failed: {e}")
        return {"error": str(e)}


# ==================== CLI ====================
def main():
    parser = argparse.ArgumentParser(description="Resume Tailor AI — Summary & Skills Only (No Company Name)")
    parser.add_argument("resume", help="Your resume file")
    parser.add_argument("jd", help="Job description file")
    parser.add_argument("-k", "--keywords", nargs="+", default=[],
                        help="Approved keywords (e.g. 'computer vision' 'image processing')")
    parser.add_argument("-o", "--output", default="output", help="Output folder")

    args = parser.parse_args()

    from extractor import extract_text_from_file
    from parser import parse_document

    print("Parsing files...")
    resume_text = extract_text_from_file(args.resume)
    jd_text = extract_text_from_file(args.jd)

    parsed_resume = parse_document(resume_text, "resume")
    parsed_jd = parse_document(jd_text, "jd")

    print(f"Adding {len(args.keywords)} approved keywords...")
    result = tailor_summary_and_skills(parsed_resume, parsed_jd, args.keywords, args.output)

    if "error" not in result:
        print("\n" + "="*60)
        print("UPDATED SUMMARY & SKILLS (NO COMPANY NAME)")
        print("="*60)
        print(open(result["updated_file"]).read())
        print("="*60)
        print(f"Skills: {len([s for s in parsed_resume.get('skills', []) if s.strip()])} → {len(result['final_skills_list'])} (+{result['added_skills_count']})")
    else:
        print("Error:", result["error"])


if __name__ == "__main__":
    main()