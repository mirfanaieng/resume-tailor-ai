# src/parser.py
import json
import re
import logging
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# === CONFIG ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("parser")

client = Groq()  # Make sure GROQ_API_KEY is in your environment!

# Try to import your existing rule-based parsers (optional fallback)
try:
    from parse_resume import parse_resume
except ImportError:
    parse_resume = None
try:
    from parse_jd import parse_jd
except ImportError:
    parse_jd = None


# ========================================
# 1. GROQ-POWERED JD & RESUME PARSER (THE MAGIC)
# ========================================
def parse_with_groq(text: str, doc_type: str = "jd") -> Dict[str, Any]:
    """Uses Groq 70B to perfectly parse JD or Resume in <1 second"""
    
    schema = {
        "jd": """
        {
          "job_title": "Senior Data Scientist",
          "company": "Farmdar",
          "location": "Lahore, Pakistan",
          "skills": ["Python", "GDAL", "Remote Sensing", "Machine Learning"],
          "responsibilities": ["Build geospatial models", "Process satellite imagery"],
          "requirements": ["5+ years in Python", "Experience with GIS tools"],
          "nice_to_have": ["AgriTech domain", "Docker"]
        }
        """,
        "resume": """
        {
          "name": "John Doe",
          "email": "john@example.com",
          "phone": "+92 300 1234567",
          "skills": ["Python", "TensorFlow", "AWS", "Docker"],
          "experience": ["Led ML team at XYZ", "Built computer vision models"],
          "education": "MS Computer Science, LUMS"
        }
        """
    }

    prompt = f"""
You are a professional ATS parser. Extract information from the following {doc_type.upper()} into valid JSON.

Return ONLY the JSON object. No explanations. No markdown.

EXAMPLE OUTPUT for {doc_type}:
{schema.get(doc_type, schema["jd"])}

TEXT:
{text[:12000]}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1024
        )
        raw = response.choices[0].message.content.strip()

        # Extract JSON block
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            logger.warning("No JSON found, returning raw")
            return {"raw_output": raw}

    except Exception as e:
        logger.error(f"Groq failed: {e}")
        return {}

def remove_garbage_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove known garbage keys that sometimes leak from rule-based parsers"""
    garbage = ["sections", "raw_text", "header", "footer", "metadata", "summary"]
    for key in garbage:
        data.pop(key, None)
    return data

# ========================================
# 2. CLEANING HELPERS
# ========================================
def clean_list(items):
    """Clean bullet points and normalize strings safely"""
    if not items:
        return []
    
    cleaned = []
    for item in items:
        if not isinstance(item, str):
            continue
        # Remove common bullet symbols safely (no invalid ranges!)
        item = re.sub(r'^[\s•*‑-–—●■▪]+', '', item.strip())   # ← FIXED
        item = re.sub(r'[\r\t]+', ' ', item)                 # clean tabs/returns
        item = re.sub(r'\s+', ' ', item).strip()             # collapse spaces
        
        # Skip garbage lines
        if len(item) < 4:
            continue
        if item.lower() in {"and", "or", "the", "to", "of", "in", "with", "experience", "skills"}:
            continue
        if item.startswith("http"):
            continue
            
        cleaned.append(item.capitalize())
    
    # Remove exact duplicates while preserving order
    seen = set()
    unique = []
    for x in cleaned:
        if x not in seen:
            seen.add(x)
            unique.append(x)
    
    return unique


# ========================================
# 3. MAIN PARSER (Smart: Rule → Groq → Clean)
# ========================================
def parse_document(text: str, doc_type: str = "resume", file_name: str = None) -> Dict[str, Any]:
    if not text or len(text) < 50:
        return {"error": "Empty or too short text"}

    logger.info(f"Parsing {doc_type.upper()} ({len(text)} chars)...")

    # Step 1: Try rule-based first (only if exists and good)
    parsed = {}
    if doc_type == "resume" and parse_resume and callable(parse_resume):
        try:
            parsed = parse_resume(text, file_name) or {}
        except:
            parsed = {}
    elif doc_type == "jd" and parse_jd and callable(parse_jd):
        try:
            parsed = parse_jd(text) or {}
        except:
            parsed = {}

    # Step 2: Always use Groq — it's better and instant
    groq_data = parse_with_groq(text, doc_type)

    # Step 3: Merge (Groq wins on conflict)
    result = {**parsed, **groq_data}

    # Step 4: Clean lists
    list_fields = ["skills", "responsibilities", "requirements", "nice_to_have", "experience"]
    for field in list_fields:
        if field in result:
            result[field] = clean_list(result[field]) if isinstance(result[field], list) else []

    # Step 5: Ensure skills is always a list of strings
    if "skills" not in result:
        result["skills"] = []
    if isinstance(result["skills"], str):
        result["skills"] = [s.strip() for s in result["skills"].split(",") if s.strip()]

    result = remove_garbage_keys(result)
    logger.info(f"Parsed {doc_type} successfully!")
    return result


# ========================================
# CLI TEST
# ========================================
if __name__ == "__main__":
    import sys
    from extractor import extract_text_from_file

    if len(sys.argv) < 3:
        print("Usage: python src/parser.py <file_path> <resume|jd>")
        sys.exit(1)

    file_path = sys.argv[1]
    doc_type = sys.argv[2].lower()

    text = extract_text_from_file(file_path)
    result = parse_document(text, doc_type=doc_type, file_name=file_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))