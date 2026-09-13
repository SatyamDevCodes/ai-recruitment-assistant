import sqlite3
import os

# Database file yahi backend folder ke andar banegi
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "recruitment.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows ko dict jaise access karne ke liye
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # candidates table: resume se extract hui basic info
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            education TEXT,
            experience_years REAL,
            skills TEXT,           -- comma separated skills
            projects TEXT,
            certifications TEXT,
            resume_filename TEXT,
            resume_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # analysis table: har candidate ki job-description ke against analysis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            job_title TEXT,
            match_score REAL,
            matching_skills TEXT,
            missing_skills TEXT,
            strengths TEXT,
            weaknesses TEXT,
            summary TEXT,
            interview_questions TEXT,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    """)

    conn.commit()
    conn.close()
