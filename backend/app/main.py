import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, get_connection
from app.resume_parser import extract_text_from_bytes
from app.llm_service import extract_candidate_info, analyze_candidate, answer_recruiter_question
from app.schemas import QuestionRequest

app = FastAPI(title="AI Recruitment Assistant API")


def _safe_number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, list):
        # list ka pehla number-jaisa item use karo
        for item in value:
            result = _safe_number(item)
            if result is not None:
                return result
        return None
    if isinstance(value, str):
        import re
        match = re.search(r"[\d.]+", value)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
    return None


def _safe_str(value):
    """List / dict ko safe string mein convert karta hai taaki SQLite error na aaye."""
    if value is None:
        return None
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else None
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value)


# CORS: React (jo alag port pe chalega, e.g. localhost:5173) ko backend
# (localhost:8000) call karne ki permission deta hai. Beginner ke liye
# yaha "*" (sabko allow) rakha hai; production me isse specific rakhna chahiye.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """App start hote hi database tables create ho jate hain."""
    init_db()


@app.get("/")
def root():
    return {"message": "AI Recruitment Assistant backend is running"}


@app.post("/api/upload-resume")
async def upload_resume(
    job_description: str = Form(...),
    job_title: str = Form("Untitled Role"),
    files: list[UploadFile] = File(...),
):
    """
    Ek ya multiple resumes upload karo, saath me job description text.
    Har resume ke liye:
      1. PDF se text extract hota hai
      2. LLM se candidate info nikalta hai
      3. LLM se JD ke against analysis hota hai
      4. Sab kuch database me save hota hai
    """
    results = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF")

        file_bytes = await file.read()

        try:
            resume_text = extract_text_from_bytes(file_bytes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract text from {file.filename}. It may be a scanned/image PDF.",
            )

        try:
            info = extract_candidate_info(resume_text)
            analysis = analyze_candidate(resume_text, job_description)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM processing failed: {e}")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO candidates
            (name, email, phone, education, experience_years, skills, projects,
             certifications, resume_filename, resume_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                info.get("name"),
                info.get("email"),
                info.get("phone"),
                _safe_str(info.get("education")),          # <-- yahan fix kiya
                _safe_number(info.get("experience_years")),
                ", ".join(info.get("skills") or []),
                ", ".join(info.get("projects") or []),
                ", ".join(info.get("certifications") or []),
                file.filename,
                resume_text,
            ),
        )
        candidate_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO analysis
            (candidate_id, job_title, match_score, matching_skills, missing_skills,
             strengths, weaknesses, summary, interview_questions, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate_id,
                job_title,
                _safe_number(analysis.get("match_score")),
                ", ".join(analysis.get("matching_skills") or []),
                ", ".join(analysis.get("missing_skills") or []),
                ", ".join(analysis.get("strengths") or []),
                ", ".join(analysis.get("weaknesses") or []),
                analysis.get("summary"),
                json.dumps(analysis.get("interview_questions") or []),
                analysis.get("recommendation"),
            ),
        )
        conn.commit()
        conn.close()

        results.append({
            "candidate_id": candidate_id,
            "filename": file.filename,
            "info": info,
            "analysis": analysis,
        })

    return {"results": results}


@app.get("/api/candidates")
def get_candidates():
    """Saare candidates + unka latest analysis return karta hai (table view ke liye)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.email, c.phone, c.education, c.experience_years,
               c.skills, c.projects, c.certifications,
               a.match_score, a.matching_skills, a.missing_skills,
               a.strengths, a.weaknesses, a.summary, a.interview_questions,
               a.recommendation
        FROM candidates c
        LEFT JOIN analysis a ON a.candidate_id = c.id
        ORDER BY a.match_score DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return {"candidates": [dict(row) for row in rows]}


@app.post("/api/ask")
def ask_question(payload: QuestionRequest):
    """
    Recruiter ka natural language question leta hai, database se saare
    candidates ka data nikaal ke LLM ko context ke roop me deta hai,
    aur AI ka jawab return karta hai.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.email, c.experience_years, c.skills,
               a.match_score, a.matching_skills, a.missing_skills,
               a.strengths, a.weaknesses, a.summary, a.recommendation
        FROM candidates c
        LEFT JOIN analysis a ON a.candidate_id = c.id
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not rows:
        return {"answer": "No candidates found in the database yet. Please upload some resumes first."}

    context_json = json.dumps(rows, indent=2, default=str)

    try:
        answer = answer_recruiter_question(payload.question, context_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {e}")

    return {"answer": answer}