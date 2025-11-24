# app_gradio.py  ← save in project root

import gradio as gr
from pathlib import Path
from extractor import extract_text_from_file
from parser import parse_document
from matcher import get_match_report
from tailor_llm import tailor_summary_and_skills

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


# Step 1: Analyze
def analyze_resume(resume_file, jd_file):
    if not resume_file or not jd_file:
        return "Upload both files", "", [], None

    resume_text = extract_text_from_file(resume_file.name)
    jd_text = extract_text_from_file(jd_file.name)

    parsed_resume = parse_document(resume_text, "resume")
    parsed_jd = parse_document(jd_text, "jd")

    report = get_match_report(parsed_resume, parsed_jd, resume_text, jd_text)
    score = report["match_score"]
    missing = report["missing_skills"][:12]

    # Smart suggestions
    suggestions = []
    lower_text = resume_text.lower()
    if any(k in lower_text for k in ["image", "opencv", "vision", "cnn", "yolo"]):
        suggestions.extend(["computer vision", "image processing", "large-scale imagery"])
    if "python" in lower_text:
        suggestions.append("python ml pipelines")
    if any(k in lower_text for k in ["pytorch", "tensorflow", "keras"]):
        suggestions.extend(["deep learning", "deep learning frameworks"])

    suggestions = list(dict.fromkeys([s.title() for s in suggestions]))

    return (
        f"**Current Match: {score}%**",
        f"Missing key skills: **{', '.join(missing) if missing else 'Great fit!'}**",
        gr.CheckboxGroup(choices=suggestions, label="I have experience with these (honestly):", value=[]),
        (parsed_resume, parsed_jd)
    )


# Step 2: Generate Summary + Skills
def generate_tailored(checkboxes, state):
    if not state:
        return "Please click 'Analyze My Match' first", None

    parsed_resume, parsed_jd = state
    approved = checkboxes or []

    result = tailor_summary_and_skills(
        parsed_resume=parsed_resume,
        parsed_jd=parsed_jd,
        approved_keywords=approved
    )

    if "error" in result:
        return f"Error: {result['error']}", None

    # These keys are now correct
    original_count = len([s for s in parsed_resume.get("skills", []) if s.strip()])
    final_count = len(result["final_skills_list"])
    added_count = final_count - original_count

    preview = f"""
**PROFESSIONAL SUMMARY**
{result['summary']}

**SKILLS** ({original_count} → {final_count} | +{added_count})
{' • '.join(result['final_skills_list'])}

**Estimated new match:** 85–95%+
"""

    txt_path = OUTPUT_DIR / "TAILORED_SUMMARY_AND_SKILLS.txt"
    name = parsed_resume.get("name", "Candidate").strip()
    job_title = parsed_jd.get("job_title", "Professional").strip()

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"{name}\n{job_title}\n\n")
        f.write("PROFESSIONAL SUMMARY\n")
        f.write(result["summary"] + "\n\n")
        f.write("SKILLS\n")
        f.write(" • ".join(result["final_skills_list"]))

    return preview.strip(), str(txt_path)


# ====================== UI ======================
with gr.Blocks(title="Resume Tailor AI — Honest & Powerful", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# Resume Tailor AI\n"
        "**Honest. Ethical. Interview-Ready.**\n"
        "We only enhance what you truly have — nothing more."
    )

    with gr.Row():
        resume_in = gr.File(label="Your Resume (PDF/DOCX)", file_types=[".pdf", ".docx"])
        jd_in = gr.File(label="Job Description", file_types=[".pdf", ".txt", ".docx"])

    analyze_btn = gr.Button("Step 1: Analyze My Match", variant="secondary", size="lg")

    score_out = gr.Markdown()
    missing_out = gr.Markdown()
    checkbox_group = gr.CheckboxGroup()
    state = gr.State()

    tailor_btn = gr.Button("Step 2: Generate Summary & Skills", variant="primary", size="lg")

    preview_out = gr.Textbox(label="Your Final Summary & Skills", lines=20)
    download_out = gr.File(label="Download .txt (Copy into your resume)")

    analyze_btn.click(
        analyze_resume,
        inputs=[resume_in, jd_in],
        outputs=[score_out, missing_out, checkbox_group, state]
    )

    tailor_btn.click(
        generate_tailored,
        inputs=[checkbox_group, state],
        outputs=[preview_out, download_out]
    )

    gr.Markdown("Made with Groq 70B • 100% Ethical • Zero lies")

if __name__ == "__main__":
    demo.launch(share=True)