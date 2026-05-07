"""Student controller"""
from models.student_model import (
    get_enrolled_classes, join_class,
    get_available_tests, get_student_submissions,
    get_leaderboard, add_leaderboard_points,
    start_submission, submit_answers
)
from models.professor_model import get_test_with_questions
from utils.session_manager import get_current_user


def get_my_classes():
    user = get_current_user()
    return get_enrolled_classes(user["id"])


def join_class_by_code(code: str) -> dict:
    user = get_current_user()
    return join_class(user["id"], code.strip().upper())


def get_tests(class_id, test_type="test"):
    user = get_current_user()
    return get_available_tests(user["id"], class_id, test_type)


def get_activities(class_id):
    return get_tests(class_id, "activity")


def get_my_scores(class_id=None):
    user = get_current_user()
    return get_student_submissions(user["id"], class_id)


def get_class_leaderboard(class_id):
    return get_leaderboard(class_id)


def begin_test(test_id):
    user = get_current_user()
    return start_submission(test_id, user["id"])


def finish_test(submission_id, answers, flagged=False, reason=""):
    result = submit_answers(submission_id, answers, flagged, reason)
    if result["ok"]:
        # Award leaderboard points for activity
        try:
            from models.database import get_connection
            conn = get_connection()
            sub = conn.execute("SELECT * FROM submissions WHERE id=?", (submission_id,)).fetchone()
            test = conn.execute("SELECT * FROM tests WHERE id=?", (sub["test_id"],)).fetchone()
            conn.close()
            if test["type"] == "activity":
                pts = int(result["percentage"] / 10)
                add_leaderboard_points(get_current_user()["id"], test["class_id"], pts)
        except Exception:
            pass
    return result


def load_test_questions(test_id):
    return get_test_with_questions(test_id)
