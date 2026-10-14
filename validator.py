# Member 2 - Validation
# Every function returns (True, clean_value) or (False, error_message)

import math
from datetime import datetime


def validate_date(text):
    text = text.strip()
    try:
        date = datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        return False, "Invalid date. Use YYYY-MM-DD, for example 2026-10-14."
    # this rejects short forms like 2026-1-5
    if len(text) != 10:
        return False, "Invalid date. Use YYYY-MM-DD, for example 2026-10-14."
    if date > datetime.today():
        return False, "Date cannot be in the future."
    return True, text


def validate_type(text):
    text = text.strip().lower()
    if text == "income" or text == "expense":
        return True, text
    return False, "Type must be income or expense."


def validate_category(text):
    text = text.strip().lower()
    if text == "":
        return False, "Category cannot be empty."
    return True, text


def validate_amount(text):
    try:
        amount = float(text.strip())
    except ValueError:
        return False, "Amount must be a number, for example 250 or 99.50."
    # this rejects nan and inf
    if not math.isfinite(amount):
        return False, "Amount must be a valid number."
    amount = round(amount, 2)
    if amount <= 0:
        return False, "Amount must be greater than 0."
    return True, amount


def validate_month(text):
    text = text.strip()
    try:
        datetime.strptime(text, "%Y-%m")
    except ValueError:
        return False, "Invalid month. Use YYYY-MM, for example 2026-10."
    if len(text) != 7:
        return False, "Invalid month. Use YYYY-MM, for example 2026-10."
    return True, text