# pip install groq langchain chromadb sentence-transformers
from os import path
from extractor import extract_text_from_file
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

client = Groq()

def score_resume_against_jd(resume_text, jd_text):
    prompt = f"""
    You are an expert recruiter. Score this resume against the job description on a scale of 0–100.
    Resume:
    {resume_text[:12000]}

    Job Description:
    {jd_text[:8000]}

    Return only: SCORE: XX/100 and one-line justification.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # ← THIS IS THE FIX
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=150
    )
    return response.choices[0].message.content

# Test it


resume_text = extract_text_from_file("data/cv.pdf")
jd_text = extract_text_from_file("data/jd.txt")
print(score_resume_against_jd(resume_text, jd_text))
