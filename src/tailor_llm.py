import requests
import json
from difflib import SequenceMatcher

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi"


def build_prompt(jd_text, resume_section):
    prompt = f"""
You are an expert resume writer.

Job Description:
{jd_text}

Resume Section:
{resume_section}

Task:
Rewrite the resume section so that it:
1. Highlights relevant skills and achievements from the job description.
2. Keeps tone professional, concise, and factual.
3. Avoids copying JD sentences directly.
4. Maintains original meaning but aligns more closely with the role.

Return only the improved section text.
"""
    return prompt.strip()

def generate_with_ollama(prompt, model=MODEL_NAME):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "").strip()
    else:
        raise Exception(f"Ollama API error: {response.text}")

def tailor_resume_sections(resume_sections, jd_text):
    tailored = {}
    for section_name, section_text in resume_sections.items():
        prompt = build_prompt(jd_text, section_text)
        improved = generate_with_ollama(prompt)
        tailored[section_name] = improved
    return tailored

def save_tailored_resume(tailored_sections, filename="tailored_resume.txt"):
    with open(filename, "w") as f:
        for section, content in tailored_sections.items():
            f.write(f"### {section.upper()}\n{content}\n\n")

def compare_sections(original, tailored):
    """
    Compare two text sections and return similarity in percentage.
    Handles NoneType, empty strings, or non-string values gracefully.
    """
    # Ensure inputs are strings
    if not isinstance(original, str):
        original = "" if original is None else str(original)
    if not isinstance(tailored, str):
        tailored = "" if tailored is None else str(tailored)

    # Handle completely missing text
    if not original.strip() and not tailored.strip():
        return 100.0   # both empty = identical
    elif not original.strip() or not tailored.strip():
        return 0.0     # one empty = no similarity

    try:
        ratio = SequenceMatcher(None, original, tailored).ratio()
        return round(ratio * 100, 2)
    except Exception as e:
        print(f"⚠️ Error comparing sections: {e}")
        return 0.0

if __name__ == "__main__":
    # load resume sections
    with open("data/jd_sample.txt") as f:
        jd_text = f.read()
    with open("data/parsed_resume.json") as f:
        resume_sections = json.load(f)  # e.g. {"Summary": "...", "Experience": "...", "Skills": "..."}

    tailored = tailor_resume_sections(resume_sections, jd_text)
    save_tailored_resume(tailored, filename="data/tailored_resume.txt")
    print("\n✅ Tailored resume saved to data/tailored_resume.txt")

    # Compare original and tailored sections
    for section, original_text in resume_sections.items():
        tailored_text = tailored.get(section, "")
        similarity = compare_sections(original_text, tailored_text)
        print(f"Section: {section} | Similarity: {similarity}%")

        


