# AI-Powered Recruitment Assistant

An end-to-end AI application that helps recruiters upload resumes, automatically
extract candidate information, score candidates against a job description, store
results in a database, and answer natural-language questions about candidates.

Built with:
- **Backend:** Python + FastAPI
- **Frontend:** React (Vite)
- **Database:** SQLite
- **PDF Parsing:** PyMuPDF
- **LLM:** Any OpenAI-compatible API (OpenAI, Groq, Together AI, OpenRouter, etc.)

---

## 1. Project Description & Objectives

Recruiters often receive hundreds of resumes per job opening. This project automates:
1. Parsing resumes (PDF) into structured data.
2. Scoring/ranking candidates against a job description using an LLM.
3. Storing candidate + analysis data in a database.
4. Answering recruiter questions in plain English (e.g. "Who knows Python?",
   "Show me the top 5 candidates").

---

## 2. System Architecture

```
 ┌────────────┐      ┌──────────────────┐      ┌───────────────────┐
 │   React    │ HTTP │     FastAPI       │      │   SQLite Database │
 │  Frontend  │◄────►│     Backend       │◄────►│  (candidates,      │
 │ (Vite,     │      │  - PDF Parsing    │      │   analysis tables) │
 │  Port 5173)│      │  - LLM calls      │      └───────────────────┘
 └────────────┘      │  - REST API       │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │   LLM Provider    │
                      │ (OpenAI/Groq/etc) │
                      └──────────────────┘
```

Flow: **Resume/JD Upload (React) → PDF Parsing (PyMuPDF) → LLM Extraction &
Scoring → SQLite Storage → Natural Language Query (LLM) → Response shown in
React UI.**

---

## 3. Folder Structure

```
ai-recruitment-assistant/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app + all API routes
│   │   ├── database.py        # SQLite connection + schema
│   │   ├── resume_parser.py   # PDF text extraction (PyMuPDF)
│   │   ├── llm_service.py     # All LLM calls (extraction, scoring, Q&A)
│   │   └── schemas.py         # Pydantic request/response models
│   ├── requirements.txt
│   └── .env.example           # Copy to .env and add your API key
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadForm.jsx      # Resume + JD upload UI
│   │   │   ├── CandidateTable.jsx  # Candidate list/table UI
│   │   │   └── AskAssistant.jsx    # Natural language Q&A chat UI
│   │   ├── api.js              # ALL fetch/axios calls to backend live here
│   │   ├── App.jsx             # Main component, wires everything together
│   │   ├── main.jsx             # React entry point
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── sample_data/
│   ├── sample_job_description.txt
│   └── (add your own sample resume PDFs here)
├── .gitignore
└── README.md
```

---

## 4. Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- An API key from any LLM provider (OpenAI, Groq, Together AI, OpenRouter, etc.)

### Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Copy the example env file and add your API key
cp .env.example .env
# Now open .env and paste your API key inside OPENAI_API_KEY=

uvicorn app.main:app --reload --port 8000
```

Backend will run at: **http://localhost:8000**

> If you use Groq/Together/OpenRouter instead of OpenAI, uncomment and set
> `OPENAI_BASE_URL` in `.env` to that provider's OpenAI-compatible endpoint.
> These providers offer generous free tiers, which is helpful since this
> project does not require a paid OpenAI key.

### Frontend Setup

Open a **new terminal** (keep backend running):

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at: **http://localhost:5173**

Open that URL in your browser — the app is now live.

---

## 5. Resume Parsing Approach

- **Library used:** PyMuPDF (`fitz`), chosen for speed, reliability, and zero
  external dependencies (no Java/Tesseract needed like some alternatives).
- Text is extracted page-by-page and concatenated.
- **Limitation:** Scanned/image-based PDFs (no embedded text layer) will not
  extract text. OCR (e.g. Tesseract) could be added as a bonus enhancement.

---

## 6. Candidate Scoring Logic & Methodology

Scoring is performed by the LLM using a structured prompt with an explicit
weighting scheme (documented in `llm_service.py`):

| Factor                              | Weight |
|--------------------------------------|--------|
| Required skills match (JD vs resume) | 60%    |
| Relevant experience (years + domain) | 25%    |
| Education / certifications relevance | 15%    |

The LLM returns a `match_score` (0–100), lists of `matching_skills` /
`missing_skills`, `strengths`, `weaknesses`, a `summary`, suggested
`interview_questions`, and a final `recommendation` (Shortlist / Consider /
Reject). This keeps scoring consistent and explainable, since the reasoning
weights are fixed in the prompt rather than left to the model's own judgment.

---

## 7. Database Schema

**candidates** table — stores extracted resume info:
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment ID |
| name, email, phone | TEXT | Contact info |
| education | TEXT | Education summary |
| experience_years | REAL | Estimated total experience |
| skills, projects, certifications | TEXT | Comma-separated lists |
| resume_filename | TEXT | Original uploaded filename |
| resume_text | TEXT | Full extracted resume text |
| created_at | TIMESTAMP | Upload time |

**analysis** table — stores JD-comparison results (linked via `candidate_id`):
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment ID |
| candidate_id | INTEGER (FK) | Links to candidates.id |
| job_title | TEXT | JD title used for this analysis |
| match_score | REAL | 0–100 score |
| matching_skills, missing_skills | TEXT | Comma-separated |
| strengths, weaknesses | TEXT | Comma-separated |
| summary | TEXT | 2-3 sentence summary |
| interview_questions | TEXT | JSON list of questions |
| recommendation | TEXT | Shortlist / Consider / Reject |
| created_at | TIMESTAMP | Analysis time |

A candidate can theoretically be analyzed against multiple job descriptions
over time (one row per analysis), supporting the "multiple JDs" bonus feature.

---

## 8. Natural Language Query Handling Approach

1. Recruiter types a question in the chat UI (`AskAssistant.jsx`).
2. Frontend sends the question to `POST /api/ask`.
3. Backend fetches **all candidates + their analysis** from SQLite.
4. This data is passed as JSON context to the LLM, along with the question.
5. The LLM is instructed to answer **only from the given context** and explain
   its reasoning (e.g., why one candidate ranks above another).

This is a simple, robust "context-stuffing" approach appropriate for a
small-to-medium number of candidates. For very large candidate pools, this
could be upgraded to a vector-database retrieval approach (see Limitations).

---

## 9. How to Run the Application

1. Start backend: `uvicorn app.main:app --reload --port 8000` (from `backend/`)
2. Start frontend: `npm run dev` (from `frontend/`)
3. Open `http://localhost:5173`
4. Paste a job description, upload resume PDF(s), click "Analyze Resumes"
5. View results in the candidate table
6. Ask questions in the chat box at the bottom

---

## 10. Assumptions Made

- LLM output is trusted to return valid JSON when explicitly instructed to;
  a fallback JSON-extraction step handles minor formatting issues.
- `experience_years` is an LLM estimate based on resume content, not a
  precisely parsed date-range calculation.
- CORS is fully open (`*`) for local development simplicity; this should be
  restricted in a production deployment.
- Only text-based (non-scanned) PDF resumes are supported out of the box.
- No authentication is implemented (assumed single-recruiter local use, per
  assignment scope); listed as a bonus item in the spec.

---

## 11. Known Limitations

- No OCR support for scanned/image-only PDF resumes.
- No vector database / semantic search — question answering relies on
  passing all candidate data as context, which may not scale to very large
  candidate pools (hundreds+) without hitting LLM context limits.
- No authentication or multi-user support.
- Match scoring depends on LLM consistency; identical resumes may get
  slightly different scores across separate runs due to LLM non-determinism
  (mitigated with `temperature=0.2`).
- No automated test suite included.

---

## 12. Tech Stack Summary

| Layer | Choice | Why |
|---|---|---|
| Backend | FastAPI | Fast, async, auto-generates API docs, beginner-friendly |
| Frontend | React (Vite) | Fast dev server, simple component model |
| Database | SQLite | Zero-config, file-based, perfect for assignment scope |
| PDF Parsing | PyMuPDF | Reliable, fast, no external system dependencies |
| LLM | OpenAI-compatible API | Flexible — works with OpenAI, Groq, Together, OpenRouter |
