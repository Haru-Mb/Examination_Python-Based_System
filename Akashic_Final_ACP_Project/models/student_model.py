"""Student model — enrollment, submissions, leaderboard"""
from models.database import get_connection
from utils.grading_system import transmute_grade
import datetime


def get_enrolled_classes(student_id):
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT c.*, u.username as professor_name
            FROM enrollments e
            JOIN classes c ON c.id=e.class_id
            JOIN users u ON u.id=c.professor_id
            WHERE e.student_id=? AND e.is_removed=0
            ORDER BY e.enrolled_at DESC
        """, (student_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def join_class(student_id, class_code) -> dict:
    conn = get_connection()
    try:
        cls = conn.execute("SELECT * FROM classes WHERE class_code=?", (class_code,)).fetchone()
        if not cls:
            return {"ok": False, "error": "Class code not found."}
        existing = conn.execute(
            "SELECT * FROM enrollments WHERE class_id=? AND student_id=?",
            (cls["id"], student_id)
        ).fetchone()
        if existing:
            if existing["is_removed"]:
                conn.execute(
                    "UPDATE enrollments SET is_removed=0 WHERE class_id=? AND student_id=?",
                    (cls["id"], student_id)
                )
                conn.commit()
                return {"ok": True, "class": dict(cls)}
            return {"ok": False, "error": "Already enrolled in this class."}
        conn.execute(
            "INSERT INTO enrollments (class_id, student_id) VALUES (?,?)",
            (cls["id"], student_id)
        )
        conn.commit()
        return {"ok": True, "class": dict(cls)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def get_available_tests(student_id, class_id, test_type="test"):
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT t.*,
                   (SELECT COUNT(*) FROM submissions s WHERE s.test_id=t.id AND s.student_id=? AND s.submitted_at IS NOT NULL) as done
            FROM tests t
            WHERE t.class_id=? AND t.type=? AND t.is_published=1
            ORDER BY t.created_at DESC
        """, (student_id, class_id, test_type)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_student_submissions(student_id, class_id=None):
    conn = get_connection()
    try:
        if class_id:
            rows = conn.execute("""
                SELECT sub.*, t.title, t.type, t.class_id
                FROM submissions sub
                JOIN tests t ON t.id=sub.test_id
                WHERE sub.student_id=? AND t.class_id=? AND sub.submitted_at IS NOT NULL
                ORDER BY sub.submitted_at DESC
            """, (student_id, class_id)).fetchall()
        else:
            rows = conn.execute("""
                SELECT sub.*, t.title, t.type, t.class_id
                FROM submissions sub
                JOIN tests t ON t.id=sub.test_id
                WHERE sub.student_id=? AND sub.submitted_at IS NOT NULL
                ORDER BY sub.submitted_at DESC
            """, (student_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_leaderboard(class_id, limit=10):
    conn = get_connection()
    try:
        today = datetime.date.today().isoformat()
        # Reset stale daily points
        conn.execute(
            "UPDATE leaderboard SET points=0, last_reset=? WHERE class_id=? AND last_reset<?",
            (today, class_id, today)
        )
        conn.commit()
        rows = conn.execute("""
            SELECT u.username, u.nickname, l.points
            FROM leaderboard l
            JOIN users u ON u.id=l.student_id
            WHERE l.class_id=?
            ORDER BY l.points DESC
            LIMIT ?
        """, (class_id, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_leaderboard_points(student_id, class_id, points):
    conn = get_connection()
    try:
        today = datetime.date.today().isoformat()
        existing = conn.execute(
            "SELECT * FROM leaderboard WHERE student_id=? AND class_id=?",
            (student_id, class_id)
        ).fetchone()
        if existing:
            if existing["last_reset"] != today:
                conn.execute(
                    "UPDATE leaderboard SET points=?, last_reset=? WHERE student_id=? AND class_id=?",
                    (points, today, student_id, class_id)
                )
            else:
                conn.execute(
                    "UPDATE leaderboard SET points=points+? WHERE student_id=? AND class_id=?",
                    (points, student_id, class_id)
                )
        else:
            conn.execute(
                "INSERT INTO leaderboard (student_id, class_id, points, last_reset) VALUES (?,?,?,?)",
                (student_id, class_id, points, today)
            )
        conn.commit()
    finally:
        conn.close()


def start_submission(test_id, student_id) -> dict:
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM submissions WHERE test_id=? AND student_id=? AND submitted_at IS NOT NULL",
            (test_id, student_id)
        ).fetchone()
        if existing:
            return {"ok": False, "error": "Already submitted."}
        # Check for in-progress
        in_progress = conn.execute(
            "SELECT * FROM submissions WHERE test_id=? AND student_id=? AND submitted_at IS NULL",
            (test_id, student_id)
        ).fetchone()
        if in_progress:
            return {"ok": True, "submission_id": in_progress["id"]}
        conn.execute(
            "INSERT INTO submissions (test_id, student_id) VALUES (?,?)",
            (test_id, student_id)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM submissions WHERE rowid=last_insert_rowid()").fetchone()
        return {"ok": True, "submission_id": row["id"]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def submit_answers(submission_id, answers: dict, is_flagged=False, flag_reason=""):
    """answers = {question_id: answer_text}"""
    conn = get_connection()
    try:
        sub = conn.execute("SELECT * FROM submissions WHERE id=?", (submission_id,)).fetchone()
        if not sub:
            return {"ok": False, "error": "Submission not found."}

        questions = conn.execute(
            "SELECT * FROM questions WHERE test_id=?", (sub["test_id"],)
        ).fetchall()

        total_score = 0
        max_score = 0

        for q in questions:
            ans_text = answers.get(q["id"], "")
            q_type = q["question_type"]
            correct = q["correct_answer"].strip().lower()
            given = ans_text.strip().lower()
            max_score += q["points"]

            is_correct = 0
            pts_earned = 0

            if q_type in ("multiple_choice", "true_false"):
                if given == correct:
                    is_correct = 1
                    pts_earned = q["points"]
            elif q_type == "short_answer":
                if given and correct and (given in correct or correct in given):
                    is_correct = 1
                    pts_earned = q["points"]
            # essay: manual grading (not auto-scored)

            total_score += pts_earned

            conn.execute("""
                INSERT INTO answers (submission_id, question_id, answer_text, is_correct, points_earned)
                VALUES (?,?,?,?,?)
            """, (submission_id, q["id"], ans_text, is_correct, pts_earned))

        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        grade_info = transmute_grade(percentage)

        conn.execute("""
            UPDATE submissions SET
                submitted_at=CURRENT_TIMESTAMP,
                total_score=?, max_score=?, percentage=?, grade=?,
                is_flagged=?, flag_reason=?
            WHERE id=?
        """, (total_score, max_score, round(percentage, 2), grade_info["grade"],
              1 if is_flagged else 0, flag_reason, submission_id))
        conn.commit()

        return {
            "ok": True,
            "percentage": round(percentage, 2),
            "grade": grade_info["grade"],
            "remarks": grade_info["remarks"],
            "total_score": total_score,
            "max_score": max_score,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()
