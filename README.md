Resume Parser & Job Description Matcher

An intelligent Resume Parsing and JD Matching System powered by Python, OCR, embeddings, and LLMs.
It extracts skills, experience, education, and matches resumes against job descriptions using semantic similarity.

⭐ Features

Upload PDF / DOCX resumes

OCR support for scanned resumes

LLM-powered parsing (Ollama / OpenAI compatible)

Extract skills, experience, projects, education

Parse Job Descriptions

Generate a Resume–JD Match Score

Gradio-based Web UI

Modular & production-ready codebase

🛠 Tech Stack

Python 3.10+

LLMs: LLaMA (Ollama), GPT (optional)

OCR: Tesseract, OpenCV

Vector DB: FAISS / SentenceTransformers

Web UI: Gradio

Parsing: pdfplumber, PyPDF2, python-docx

📦 Installation
1. Clone the repo
git clone https://github.com/yourusername/resume-parser.git
cd resume-parser

2. Create virtual environment
python -m venv .venv


Activate:

Windows

.venv\Scripts\activate


Linux/Mac

source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. (Optional) Install Tesseract OCR

Linux:

sudo apt install tesseract-ocr


Windows: Install from official site.

▶️ Run the App
Gradio Web UI
python src/app_gradio.py

Parse a Resume (CLI)
python src/parse_resume.py --file samples/resume.pdf

📁 Project Structure
resume-parser/
│
├── src/
│   ├── extractor.py        # Extract text from PDF, DOCX, OCR
│   ├── parser_llm.py       # Parse resume using LLM
│   ├── jd_matcher.py       # Match resume with job description
│   ├── embeddings.py       # Vector similarity
│   ├── utils.py
│   └── app_gradio.py       # Web UI
│
├── examples/
├── requirements.txt
├── README.md
└── .gitignore

⚙️ Environment Variables (Optional)

Create a .env file:

OPENAI_API_KEY=your_key
OLLAMA_MODEL=llama3.2
EMBEDDING_MODEL=all-MiniLM-L6-v2

🎯 How Matching Works

Extract raw resume text

Parse structured fields using an LLM

Extract keywords from JD

Compute:

Skills similarity

Keyword overlap

Embedding similarity

Generate a final 0–100 match score

Provide a breakdown explanation

🚧 Roadmap

 Add Docker support

 Export results to PDF

 Multi-language support

 ATS compatibility checker

 JD auto-generation

🤝 Contributing

Fork the repo

Create a new branch

Commit your changes

Submit a pull request
