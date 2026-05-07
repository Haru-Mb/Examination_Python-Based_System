# Examination_Python-Based_System
The Akashic Examination System is a Python and Tkinter-based desktop application designed to modernize academic examinations. It features secure student and professor login systems, digital exam management, and an interactive GUI that improves efficiency, organization, and user experience.
Akashik — Examination System
A modern, minimalist Python/Tkinter examination platform built for Philippine academic standards.

Features
Student Module
Home Dashboard — profile card, progress tracker, summary stats, class leaderboard, weekly report
Activities — Kahoot-style timed quizzes with auto-scoring and leaderboard points
Tests — Google-Forms-style secure exams with anti-cheat window detection
Scores — Full history of submissions with grades using PH CHED transmutation
Join Class — Enter a professor's unique class code to access materials
Professor Module
Home — Class overview with enrolled students and class codes displayed
Create — Build tests/activities with multiple question types (MC, T/F, Short Answer, Essay)
Student Data — View all student grades, ranks, submission counts; remove unauthorized students
Flagged — Review students flagged for cheating on tests/activities
System Features
🌗 Light / Dark mode toggle
🔒 Anti-cheat: window focus loss flags exam submissions automatically
🏆 Daily leaderboard reset (resets at midnight per day)
📊 Philippine CHED grading (1.00–5.00 transmutation)
🔑 9–11 character unique class codes for secure enrollment
📧 Email verification (stub — configure SMTP in config.py for production)
🗄️ SQLite database (zero external dependencies beyond Python stdlib + tkinter)
Requirements
Python 3.10+
tkinter (included with most Python installs)
No external pip packages required
Setup & Run
# Clone or extract the project
cd akashik

# Run directly
python main.py
Quick Start (Demo Data)
Run the seed script to create demo accounts:

python seed.py
This creates:

Role	Username	Password	SR Code
Professor	prof_demo	Demo@1234	PROF-0001
Student	student1	Demo@1234	2024-00001
Student	student2	Demo@1234	2024-00002
The professor account will have a demo class pre-created with a published test and activity.

Project Structure
akashik/
├── main.py                  # Entry point
├── config.py                # App constants & theme colors
├── seed.py                  # Demo data seeder
│
├── models/
│   ├── database.py          # SQLite schema & connection
│   ├── user_model.py        # Auth, profile
│   ├── student_model.py     # Enrollment, leaderboard, scores
│   ├── professor_model.py   # Class/test/grade management
│   └── score_model.py       # Submission & answer handling
│
├── views/
│   ├── home_view.py         # Landing page
│   ├── auth_view.py         # Login / signup
│   ├── student_dashboard_view.py   # Full student UI
│   ├── professor_dashboard_view.py # Full professor UI
│   └── components/
│       ├── theme.py         # Design system / light-dark
│       ├── sidebar.py       # Navigation sidebar
│       └── modal.py         # Dialogs & confirmations
│
├── controllers/
│   ├── auth_controller.py
│   ├── student_controller.py
│   ├── professor_controller.py
│   ├── test_controller.py
│   ├── activity_controller.py
│   ├── leaderboard_controller.py
│   └── cheat_detection_controller.py
│
├── utils/
│   ├── code_generator.py    # Unique class code generation
│   ├── grading_system.py    # PH CHED transmutation
│   ├── validator.py         # Input validation
│   ├── session_manager.py   # Login session state
│   └── email_service.py     # Email verification (configurable)
│
└── database/
    └── akashik.db           # Auto-created on first run
Grading System (Philippine CHED)
Score Range	Grade	Remarks
99–100	1.00	Excellent
96–98	1.25	Excellent
93–95	1.50	Very Good
90–92	1.75	Very Good
87–89	2.00	Good
84–86	2.25	Good
81–83	2.50	Satisfactory
78–80	2.75	Satisfactory
75–77	3.00	Passing
0–74	5.00	Failed
Configuration (config.py)
Setting	Description
EMAIL_ENABLED	Set True + fill credentials for email
EMAIL_USER	Gmail address for sending emails
EMAIL_PASS	Gmail app password
SESSION_TIMEOUT_MINUTES	Auto-logout timeout
Anti-Cheat System
During a Test (not activity):

The exam opens in a dedicated window with grab_set() focus lock
If the student clicks outside, minimizes, or alt-tabs → FocusOut event fires
The submission is immediately flagged with reason "Window focus lost"
A red warning overlay appears; the student may continue but remains flagged
Professor sees flagged submissions in the ⚠ Flagged section
