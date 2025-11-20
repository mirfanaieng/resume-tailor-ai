# app_gradio.py

import gradio as gr
import json
import os
from src.extractor import extract_text_from_file
from src.parser import parse_resume
from src.matcher import match_skills
from src.tailor_llm import tailor_resume_sections
from src.formatter import create_formatted_resume_from_txt

# Ensure output folder exists
os.makedirs("data", exist_ok=True)

def process_resume(resume_file, jd_file):
    # 1️⃣ Extract text
    resume_text = extract_text_from_file(resume_file.name)
    jd_text = extract_text_from_file(jd_file.name)

    # 2️⃣ Parse sections
    resume_sections = parse_resume(resume_text)
    jd_sections = parse_resume(jd_text)

    # 3️⃣ Match skills
    match_report = match_skills(resume_sections.get("Skills", ""), jd_sections.get("Skills", ""))
    match_score = f"{match_report['match_score']}% match"
    missing_skills = ", ".join(match_report["missing_skills"]) if match_report["missing_skills"] else "None"

    # 4️⃣ Generate tailored resume text
    tailored_resume_dict = tailor_resume_sections(resume_sections, jd_sections)

    # 5️⃣ Save tailored resume to .txt temporarily
    temp_txt_path = "data/temp_tailored_resume.txt"
    with open(temp_txt_path, "w", encoding="utf-8") as f:
        for section, content in tailored_resume_dict.items():
            f.write(f"=== {section.upper()} ===\n{content.strip()}\n\n")


    # 6️⃣ Convert to .docx
    docx_path = create_formatted_resume_from_txt(temp_txt_path)
    # Convert dict into a readable string for Gradio preview
    tailored_text_preview = ""
    for section, content in tailored_resume_dict.items():
        tailored_text_preview += f"\n\n=== {section.upper()} ===\n{content.strip()}"

    return match_score, missing_skills, tailored_text_preview.strip(), docx_path

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## Resume Tailor AI")
    with gr.Row():
        resume_input = gr.File(label="Upload Resume (.txt/.pdf/.docx)")
        jd_input = gr.File(label="Upload Job Description (.txt/.pdf/.docx)")
    submit_btn = gr.Button("Tailor Resume")
    match_score_output = gr.Textbox(label="Skill Match Score")
    missing_skills_output = gr.Textbox(label="Missing Skills")
    tailored_preview = gr.Textbox(label="Tailored Resume Preview", lines=15)
    download_btn = gr.File(label="Download Tailored Resume (.docx)")

    submit_btn.click(
        fn=process_resume,
        inputs=[resume_input, jd_input],
        outputs=[match_score_output, missing_skills_output, tailored_preview, download_btn]
    )

demo.launch()
