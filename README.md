# 📄 Resume Parser and Job Description Matcher

A complete **Resume Parsing and Job Description (JD) Matching system** built using Python, OCR, and LLM-based text extraction.  
It parses resume text, extracts structured information, and calculates a match score against job descriptions.

---

## ✨ Features

- Upload PDF or DOCX resumes  
- OCR support for scanned resumes  
- LLM-based structured resume parsing  
- Extract skills, experience, education, projects  
- Parse and analyze job descriptions  
- Generate Resume–JD match score  
- Gradio-based web interface  
- Modular and extensible codebase  

---

## 🧰 Technology Stack

- **Python 3.10+**
- **OCR:** Tesseract, OpenCV  
- **LLMs:** LLaMA via Ollama, OpenAI-compatible models  
- **Vector Similarity:** FAISS or SentenceTransformers  
- **UI:** Gradio  
- **File Parsing:** pdfplumber, PyPDF2, python-docx  

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/resume-parser.git
cd resume-parser


2. Create a virtual environment
  python -m venv .venv


Activate the environment:

Windows
.venv\Scripts\activate
Mac/Linux
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

▶️ Usage
Run the Gradio Web App
python src/app_gradio.py

Parse a resume using CLI
python src/parse_resume.py --file samples/resume.pdf

📁 Project Structure
resume-parser/
│
├── src/
│   ├── extractor.py        # Extract text from PDF/DOCX/OCR
│   ├── parser_llm.py       # LLM-based resume parsing
│   ├── jd_matcher.py       # JD similarity and scoring
│   ├── embeddings.py       # Vector similarity functions
│   ├── utils.py
│   └── app_gradio.py       # Web interface
│
├── examples/
├── requirements.txt
├── README.md
└── .gitignore


🔍 How It Works

Extract raw resume text (PDF, DOCX, or OCR)

Use LLMs to convert text into structured fields

Extract important keywords from the job description

Compute similarity using:

Skills matching

Keyword overlap

Embedding similarity

Produce a match score (0–100)

Provide a detailed score breakdown

🗺️ Roadmap

 Add Docker support

 Add PDF export for reports

 Add ATS compliance checker

 Add multilingual resume parsing

 Improve JD keyword extraction

🤝 Contributing

Fork the repository

Create a new feature branch

Commit your changes

Submit a pull request
