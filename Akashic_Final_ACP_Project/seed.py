"""
Akashik — Demo Data Seeder
Run: python seed.py
Creates demo professor + students + class + test + activity
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db
from models.user_model import create_user, get_user_by_login
from models.professor_model import (
    create_class, create_test, add_question, publish_test
)
from models.student_model import join_class

DEMO_PASSWORD = "Demo@1234"

def seed():
    print("🌱  Akashik Seeder")
    print("─" * 40)
    init_db()

    # Professor
    r = create_user("prof_demo", "prof@akashik.local", "PROF-0001", DEMO_PASSWORD, "professor")
    if r["ok"]:
        print("✓  Professor created: prof_demo / Demo@1234")
    else:
        print(f"   Professor: {r['error']}")

    # Students
    for i in range(1, 4):
        r = create_user(
            f"student{i}", f"student{i}@akashik.local",
            f"2024-0000{i}", DEMO_PASSWORD, "student"
        )
        if r["ok"]:
            print(f"✓  Student created: student{i} / Demo@1234")
        else:
            print(f"   Student {i}: {r['error']}")

    # Get professor
    prof = get_user_by_login("prof_demo", DEMO_PASSWORD)
    if not prof:
        print("✗  Could not retrieve professor. Aborting.")
        return

    # Create class
    cls_result = create_class(prof["id"], "BSIT 301 — Software Engineering", "Demo class for Akashik")
    if cls_result["ok"]:
        cls = cls_result["class"]
        print(f"✓  Class created: '{cls['name']}'")
        print(f"   Class Code: {cls['class_code']}")
    else:
        print(f"   Class: {cls_result['error']}")
        return

    # Enroll students
    for i in range(1, 4):
        s = get_user_by_login(f"student{i}", DEMO_PASSWORD)
        if s:
            r = join_class(s["id"], cls["class_code"])
            if r["ok"]:
                print(f"✓  student{i} enrolled in class")

    # Create a test
    test_result = create_test(
        cls["id"], prof["id"],
        "Midterm Examination",
        "BSIT 301 midterm — covers software lifecycle and design patterns",
        "test", time_limit=60
    )
    if test_result["ok"]:
        tid = test_result["test"]["id"]
        print(f"✓  Test created: 'Midterm Examination'")
        import json
        add_question(tid, "What does SDLC stand for?", "multiple_choice",
                     json.dumps(["Software Development Life Cycle",
                                 "System Design and Logic Control",
                                 "Structured Data Language Construct",
                                 "Software Deployment and Launch Cycle"]),
                     "Software Development Life Cycle", 2, 1)
        add_question(tid, "The Waterfall model allows going back to previous phases easily.", "true_false",
                     "", "False", 1, 2)
        add_question(tid, "Name one advantage of Agile over Waterfall.", "short_answer",
                     "", "flexibility", 3, 3)
        add_question(tid, "Explain what a design pattern is and give one example.", "essay",
                     "", "", 5, 4)
        publish_test(tid)
        print("✓  Midterm test published with 4 questions")

    # Create an activity
    act_result = create_test(
        cls["id"], prof["id"],
        "Week 3 Quiz — Agile Basics",
        "Quick Kahoot-style review",
        "activity", time_limit=0
    )
    if act_result["ok"]:
        aid = act_result["test"]["id"]
        print(f"✓  Activity created: 'Week 3 Quiz'")
        import json
        add_question(aid, "Agile is an iterative development approach.", "true_false",
                     "", "True", 1, 1)
        add_question(aid, "Which of the following is an Agile framework?", "multiple_choice",
                     json.dumps(["Scrum","Waterfall","V-Model","Big Bang"]),
                     "Scrum", 1, 2)
        add_question(aid, "How many phases does a typical Sprint have?", "multiple_choice",
                     json.dumps(["2","3","4","5"]),
                     "4", 1, 3)
        add_question(aid, "A Product Backlog is maintained by the Scrum Master.", "true_false",
                     "", "False", 1, 4)
        add_question(aid, "What does MVP stand for in Agile?", "short_answer",
                     "", "Minimum Viable Product", 2, 5)
        publish_test(aid)
        print("✓  Activity published with 5 questions")

    print()
    print("═" * 40)
    print("  Seeding complete! Launch with: python main.py")
    print()
    print("  Login credentials:")
    print(f"  Professor → prof_demo / {DEMO_PASSWORD}")
    print(f"  Students  → student1–3 / {DEMO_PASSWORD}")
    print(f"  Class Code → {cls['class_code']}")
    print("═" * 40)


if __name__ == "__main__":
    seed()
