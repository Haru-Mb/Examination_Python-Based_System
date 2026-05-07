"""Professor model - class management, student data"""
from models.database import get_connection
from utils.code_generator import generate_class_code


def create_class(professor_id, name, description="") -> dict:
    conn = get_connection()
    try:
        code = generate_class_code()
        while conn.execute("SELECT 1 FROM classes WHERE class_code=?", (code,)).fetchone():
            code = generate_class_code()
        conn.execute(
            "INSERT INTO classes (professor_id, class_code, name, description) VALUES (?,?,?,?)",
            (professor_id, code, name, description)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM classes WHERE class_code=?", (code,)).fetchone()
        return {"ok": True, "class": dict(row)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def get_professor_classes(professor_id):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM classes WHERE professor_id=? ORDER BY created_at DESC",
            (professor_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_class_students(class_id):
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT u.id, u.username, u.email, u.sr_code, u.nickname, e.enrolled_at, e.is_removed
            FROM enrollments e
            JOIN users u ON u.id=e.student_id
            WHERE e.class_id=?
            ORDER BY u.username
        """, (class_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def remove_student(class_id, student_id):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE enrollments SET is_removed=1 WHERE class_id=? AND student_id=?",
            (class_id, student_id)
        )
        conn.commit()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def get_student_grades(class_id):
    """Get all student grades for a class with Philippine grading"""
    conn = get_connection()
    try:
        students = conn.execute("""
            SELECT u.id, u.username, u.sr_code, u.nickname
            FROM enrollments e
            JOIN users u ON u.id=e.student_id
            WHERE e.class_id=? AND e.is_removed=0
        """, (class_id,)).fetchall()

        result = []
        for s in students:
            subs = conn.execute("""
                SELECT percentage, is_flagged, type
                FROM submissions sub
                JOIN tests t ON t.id=sub.test_id
                WHERE sub.student_id=? AND t.class_id=? AND sub.submitted_at IS NOT NULL
            """, (s["id"], class_id)).fetchall()

            test_scores = [r["percentage"] for r in subs if r["type"] == "test"]
            act_scores  = [r["percentage"] for r in subs if r["type"] == "activity"]
            flagged = sum(1 for r in subs if r["is_flagged"])

            avg = (sum(test_scores + act_scores) / len(test_scores + act_scores)) if (test_scores or act_scores) else 0

            from utils.grading_system import transmute_grade
            grade_info = transmute_grade(avg)

            result.append({
                **dict(s),
                "avg_score": round(avg, 2),
                "grade": grade_info["grade"],
                "remarks": grade_info["remarks"],
                "test_count": len(test_scores),
                "activity_count": len(act_scores),
                "flagged_count": flagged,
            })

        # Rank students
        result.sort(key=lambda x: x["avg_score"], reverse=True)
        for i, r in enumerate(result):
            r["rank"] = i + 1

        return result
    finally:
        conn.close()


def get_flagged_students(class_id):
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT u.username, u.sr_code, t.title, t.type,
                   sub.submitted_at, sub.flag_reason
            FROM submissions sub
            JOIN users u ON u.id=sub.student_id
            JOIN tests t ON t.id=sub.test_id
            WHERE t.class_id=? AND sub.is_flagged=1
            ORDER BY sub.submitted_at DESC
        """, (class_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_test(class_id, professor_id, title, description, test_type, time_limit=0) -> dict:
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO tests (class_id,professor_id,title,description,type,time_limit)
            VALUES (?,?,?,?,?,?)
        """, (class_id, professor_id, title, description, test_type, time_limit))
        conn.commit()
        row = conn.execute("SELECT * FROM tests WHERE rowid=last_insert_rowid()").fetchone()
        return {"ok": True, "test": dict(row)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def add_question(test_id, text, q_type, options, correct, points, order_num):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO questions (test_id,question_text,question_type,options,correct_answer,points,order_num)
            VALUES (?,?,?,?,?,?,?)
        """, (test_id, text, q_type, options, correct, points, order_num))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def get_tests_for_class(class_id, test_type=None):
    conn = get_connection()
    try:
        if test_type:
            rows = conn.execute(
                "SELECT * FROM tests WHERE class_id=? AND type=? ORDER BY created_at DESC",
                (class_id, test_type)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tests WHERE class_id=? ORDER BY created_at DESC",
                (class_id,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_test_with_questions(test_id):
    conn = get_connection()
    try:
        test = conn.execute("SELECT * FROM tests WHERE id=?", (test_id,)).fetchone()
        if not test:
            return None
        questions = conn.execute(
            "SELECT * FROM questions WHERE test_id=? ORDER BY order_num",
            (test_id,)
        ).fetchall()
        return {"test": dict(test), "questions": [dict(q) for q in questions]}
    finally:
        conn.close()


def publish_test(test_id):
    conn = get_connection()
    try:
        conn.execute("UPDATE tests SET is_published=1 WHERE id=?", (test_id,))
        conn.commit()
    finally:
        conn.close()
