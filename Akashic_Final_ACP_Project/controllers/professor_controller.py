"""Professor controller"""
from models.professor_model import (
    get_professor_classes, create_class,
    get_class_students, remove_student,
    get_student_grades, get_flagged_students,
    create_test, add_question, get_tests_for_class,
    get_test_with_questions, publish_test
)
from utils.session_manager import get_current_user


def get_my_classes():
    user = get_current_user()
    return get_professor_classes(user["id"])


def create_new_class(name, description="") -> dict:
    user = get_current_user()
    return create_class(user["id"], name, description)


def get_students(class_id):
    return get_class_students(class_id)


def kick_student(class_id, student_id) -> dict:
    return remove_student(class_id, student_id)


def get_grades(class_id):
    return get_student_grades(class_id)


def get_flagged(class_id):
    return get_flagged_students(class_id)


def create_new_test(class_id, title, description, test_type, time_limit=0) -> dict:
    user = get_current_user()
    return create_test(class_id, user["id"], title, description, test_type, time_limit)


def add_test_question(test_id, text, q_type, options, correct, points, order_num) -> dict:
    return add_question(test_id, text, q_type, options, correct, points, order_num)


def get_class_tests(class_id, test_type=None):
    return get_tests_for_class(class_id, test_type)


def get_full_test(test_id):
    return get_test_with_questions(test_id)


def publish(test_id):
    publish_test(test_id)
    return {"ok": True}
