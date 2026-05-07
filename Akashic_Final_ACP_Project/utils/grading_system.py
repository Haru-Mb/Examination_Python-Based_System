"""Philippine CHED grading system"""
from config import GRADE_TRANSMUTATION


def transmute_grade(percentage: float) -> dict:
    for (low, high), (grade, remarks) in GRADE_TRANSMUTATION.items():
        if low <= percentage <= high:
            return {"grade": grade, "remarks": remarks, "percentage": round(percentage, 2)}
    return {"grade": "5.00", "remarks": "Failed", "percentage": round(percentage, 2)}


def get_grade_color(grade: str) -> str:
    """Return color string based on grade for UI display"""
    g = float(grade)
    if g <= 1.50:
        return "success"
    elif g <= 2.50:
        return "accent"
    elif g <= 3.00:
        return "warning"
    else:
        return "danger"
