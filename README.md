📄 Resume Parser & Job Description Matcher

An intelligent Resume Parsing and JD Matching System built with Python, OCR, and LLM-powered text extraction.
This project extracts structured information from resumes, analyzes job descriptions, and calculates a match score to help candidates or recruiters quickly evaluate fit.

🚀 Features

📤 Upload PDF/DOCX resumes

🔍 OCR support for scanned resumes using Tesseract/OpenCV

🤖 LLM-powered text parsing → Name, email, skills, experience, education

📝 Job Description extraction

🎯 Resume–JD Matching Score

📊 Similarity breakdown: skills, experience, keywords

⚡ Gradio-based Web UI for fast interaction

🧩 Modular code for easy extension

🐍 Works with Ollama, LLaMA, or OpenAI-compatible models

🛠️ Tech Stack

Python 3.10+

OCR: Tesseract / OpenCV

LLMs: phi: Latest

Vector Search: FAISS / sentence-transformers

Web UI: Gradio

Parsing: PyPDF2, pdfplumber, docx

Backend Utilities: LangChain (optional)

📦 Installation
1️⃣ Clone repository
git clone https://github.com/mirfanaieng/resume-tailor-ai.git


2️⃣ Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # Mac/Linux
.venv\Scripts\activate          # Windows

3️⃣ Install dependencies
pip install -r requirements.txt


If using Tesseract OCR:

sudo apt install tesseract-ocr   # Ubuntu


Windows users: download Tesseract installer.

▶️ Usage
Run Gradio App
python src/app_gradio.py

Or run CLI parsing
python src/parse_resume.py --file sample_resume.pdf

📁 Project Structure
resume-parser/
│── src/
│   ├── extractor.py         # PDF/Text extraction
│   ├── parser_llm.py        # LLM-based resume parsing
│   ├── jd_matcher.py        # Job description matcher
│   ├── embeddings.py        # Vector similarity
│   ├── utils.py
│   ├── app_gradio.py        # Web UI
│── examples/
│── requirements.txt
│── README.md
│── .gitignore

⚙️ Environment Variables (Optional)

Create .env file:

OPENAI_API_KEY=your_key (optional)
OLLAMA_MODEL=llama3.2
EMBEDDING_MODEL=all-MiniLM-L6-v2

🎯 How Matching Works

Extract resume text
→ PDF, DOCX, or OCR-based extraction

Parse into structured fields using an LLM

Extract JD keywords

Calculate similarity using:

Skills match

Keyword overlap

Vector embeddings

Generate match score (0–100)

Return explanation breakdown

📸 Screenshots (Optional)

Add UI screenshots or GIFs.


🛠️ Roadmap

 Improve OCR for low-quality resumes

 Add multilingual resume support

 AI-based JD suggestion

 ATS compliance checker

 Export results to PDF

 Add Docker container support

🤝 Contributing

Contributions are welcome!

Fork this repo

Create a feature branch

Commit changes

Create a pull request
