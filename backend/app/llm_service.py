import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")  # None means default OpenAI endpoint
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Client sirf ek baar banate hain
if BASE_URL:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
else:
    client = OpenAI(api_key=API_KEY)


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """Common helper: LLM ko call karke sirf text response return karta hai."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def _safe_json_parse(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json\n", "", 1).replace("json", "", 1)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)


def extract_candidate_info(resume_text: str) -> dict:
    """Resume ke raw text se structured candidate info nikalta hai."""
    system_prompt = (
        "You are a resume parsing assistant. Extract structured information "
        "from the resume text. Always reply with ONLY valid JSON, no extra text."
    )
    user_prompt = f"""
Extract the following fields from this resume text and return as JSON with these exact keys:
name, email, phone, education, experience_years (a number, estimate total years),
skills (a list of strings), projects (a list of strings), certifications (a list of strings).

If a field is not found, use null or an empty list.

Resume text:
\"\"\"
{resume_text}
\"\"\"
"""
    raw = _call_llm(system_prompt, user_prompt)
    return _safe_json_parse(raw)


def analyze_candidate(resume_text: str, job_description: str) -> dict:
    """Resume ko job description ke against compare karke score/analysis deta hai."""
    system_prompt = (
        "You are an expert technical recruiter AI. You evaluate resumes against "
        "job descriptions fairly and consistently. Always reply with ONLY valid JSON."
    )
    user_prompt = f"""
Compare this resume against the job description and return a JSON object with these exact keys:

- match_score: a number from 0 to 100
- matching_skills: list of skills from the JD that the candidate has
- missing_skills: list of skills from the JD that the candidate is missing
- strengths: list of short strings
- weaknesses: list of short strings
- summary: a 2-3 sentence candidate summary
- interview_questions: list of 3-5 suggested interview questions specific to this candidate
- recommendation: one of "Shortlist", "Consider", "Reject"

Scoring guidance (document this logic, it should be followed consistently):
- Required skills match = 60% weight
- Relevant experience (years + domain relevance) = 25% weight
- Education/certifications relevance = 15% weight

Job Description:
\"\"\"
{job_description}
\"\"\"

Resume:
\"\"\"
{resume_text}
\"\"\"
"""
    raw = _call_llm(system_prompt, user_prompt)
    return _safe_json_parse(raw)


def answer_recruiter_question(question: str, candidates_context: str) -> str:
    """
    Recruiter ke natural language question ka jawab deta hai, candidates ke
    stored data (candidates_context) ko context ke roop me use karke.
    """
    system_prompt = (
        "You are a helpful AI recruitment assistant. You answer recruiter "
        "questions about candidates using ONLY the data provided in the context. "
        "Give clear, concise answers and explain your reasoning when relevant "
        "(e.g. why one candidate ranks above another). If the answer isn't in "
        "the context, say so honestly."
    )
    user_prompt = f"""
Here is the candidate data (JSON list):
{candidates_context}

Recruiter's question: {question}

Answer the question clearly and concisely based on the data above.
"""
    return _call_llm(system_prompt, user_prompt)
