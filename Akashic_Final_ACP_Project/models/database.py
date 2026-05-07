"""
Database initialization and connection management
"""
import sqlite3
import os
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = get_connection()
    c = conn.cursor()

    # Users
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        sr_code TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student','professor')),
        is_verified INTEGER DEFAULT 0,
        verification_token TEXT,
        profile_photo TEXT DEFAULT '',
        nickname TEXT DEFAULT '',
        bio TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )""")

    # Classes
    c.execute("""CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor_id INTEGER NOT NULL,
        class_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(professor_id) REFERENCES users(id)
    )""")

    # Class enrollments
    c.execute("""CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_removed INTEGER DEFAULT 0,
        FOREIGN KEY(class_id) REFERENCES classes(id),
        FOREIGN KEY(student_id) REFERENCES users(id),
        UNIQUE(class_id, student_id)
    )""")

    # Tests / Quizzes
    c.execute("""CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER NOT NULL,
        professor_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        type TEXT NOT NULL CHECK(type IN ('test','activity')),
        time_limit INTEGER DEFAULT 0,
        is_published INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(class_id) REFERENCES classes(id),
        FOREIGN KEY(professor_id) REFERENCES users(id)
    )""")

    # Questions
    c.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        question_type TEXT NOT NULL CHECK(question_type IN ('multiple_choice','true_false','short_answer','essay')),
        options TEXT DEFAULT '',
        correct_answer TEXT DEFAULT '',
        points INTEGER DEFAULT 1,
        order_num INTEGER DEFAULT 0,
        FOREIGN KEY(test_id) REFERENCES tests(id)
    )""")

    # Student answers / submissions
    c.execute("""CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        submitted_at TIMESTAMP,
        is_flagged INTEGER DEFAULT 0,
        flag_reason TEXT DEFAULT '',
        total_score REAL DEFAULT 0,
        max_score REAL DEFAULT 0,
        percentage REAL DEFAULT 0,
        grade TEXT DEFAULT '',
        FOREIGN KEY(test_id) REFERENCES tests(id),
        FOREIGN KEY(student_id) REFERENCES users(id)
    )""")

    # Answers
    c.execute("""CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        answer_text TEXT DEFAULT '',
        is_correct INTEGER DEFAULT 0,
        points_earned REAL DEFAULT 0,
        FOREIGN KEY(submission_id) REFERENCES submissions(id),
        FOREIGN KEY(question_id) REFERENCES questions(id)
    )""")

    # Leaderboard points
    c.execute("""CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        points INTEGER DEFAULT 0,
        last_reset DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY(student_id) REFERENCES users(id),
        FOREIGN KEY(class_id) REFERENCES classes(id),
        UNIQUE(student_id, class_id)
    )""")

    # Sessions
    c.execute("""CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    # Weekly reports cache
    c.execute("""CREATE TABLE IF NOT EXISTS weekly_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        week_start DATE NOT NULL,
        activities_done INTEGER DEFAULT 0,
        tests_done INTEGER DEFAULT 0,
        avg_score REAL DEFAULT 0,
        total_points INTEGER DEFAULT 0,
        FOREIGN KEY(student_id) REFERENCES users(id),
        FOREIGN KEY(class_id) REFERENCES classes(id)
    )""")

    conn.commit()
    conn.close()
