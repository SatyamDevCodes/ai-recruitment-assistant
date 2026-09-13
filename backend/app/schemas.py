from pydantic import BaseModel
from typing import Optional


class QuestionRequest(BaseModel):
    question: str


class CandidateResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: Optional[str] = None
    experience_years: Optional[float] = None
    skills: Optional[str] = None
    projects: Optional[str] = None
    certifications: Optional[str] = None
    match_score: Optional[float] = None
    matching_skills: Optional[str] = None
    missing_skills: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    summary: Optional[str] = None
    interview_questions: Optional[str] = None
    recommendation: Optional[str] = None
