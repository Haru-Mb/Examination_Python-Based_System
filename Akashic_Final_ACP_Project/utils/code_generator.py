"""Generate unique class codes"""
import random
import string
from config import CLASS_CODE_MIN_LEN, CLASS_CODE_MAX_LEN


def generate_class_code() -> str:
    length = random.randint(CLASS_CODE_MIN_LEN, CLASS_CODE_MAX_LEN)
    chars = string.ascii_uppercase + string.digits
    # Ensure at least 2 digits and 2 letters
    code = (
        random.choices(string.ascii_uppercase, k=2) +
        random.choices(string.digits, k=2) +
        random.choices(chars, k=length - 4)
    )
    random.shuffle(code)
    return "".join(code)
