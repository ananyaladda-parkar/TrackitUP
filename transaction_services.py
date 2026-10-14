# Member 4 - Transaction service
# This is the only file that talks to validator, storage and reports.

import reports
import storage
import validator

SAVE_ERROR = "Could not save transactions.csv. Is it open in Excel?"


def balance_warning(transactions):
    balance = reports.get_summary(transactions)["balance"]
    if balance < 0:
        return "\nWARNING: your balance is negative (" + str(balance) + ")."
    return ""


def add_transaction(date, type_, category, amount, note=""):
    ok, result = validator.validate_date(date)
    if not ok:
        return False, result
    date = result

    ok, result = validator.validate_type(type_)
    if not ok:
        return False, result
    type_ = result

    ok, result = validator.validate_category(category)
    if not ok:
        return False, result
    category = result

    ok, result = validator.validate_amount(amount)
    if not ok:
        return False, result
    amount = result

    transactions = storage.load_transactions()
    new_transaction = {
        "date": date,
        "type": type_,
        "category": category,
        "amount": amount,
        "note": note.strip(),
    }
    transactions.append(new_transaction)

    if not storage.save_transactions(transactions):
        return False, SAVE_ERROR
    return True, "Transaction added." + balance_warning(transactions)


def get_all_transactions():
    return storage.load_transactions()


def delete_transaction(index):
    # index is the number shown in the list (it starts from 1)
    try:
        index = int(index.strip())
    except ValueError:
        return False, "Please enter a valid number."

    transactions = storage.load_transactions()
    if index < 1 or index > len(transactions):
        return False, "No transaction with number " + str(index) + "."

    removed = transactions.pop(index - 1)
    if not storage.save_transactions(transactions):
        return False, SAVE_ERROR
    message = "Deleted: " + removed["date"] + " " + removed["category"] + " " + str(removed["amount"])
    return True, message + balance_warning(transactions)


def summary():
    return reports.get_summary(storage.load_transactions())


def category_report():
    transactions = storage.load_transactions()
    return {
        "expense": reports.get_category_totals(transactions, "expense"),
        "income": reports.get_category_totals(transactions, "income"),
    }


def monthly_report(month):
    # returns (True, summary) or (False, error message)
    ok, result = validator.validate_month(month)
    if not ok:
        return False, result
    return True, reports.get_monthly_summary(storage.load_transactions(), result)


def largest_expense():
    return reports.get_largest_expense(storage.load_transactions())