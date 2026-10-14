"""Member 5 - Reports. Pure functions: take a list, return results. No input(), print() or files."""


def get_summary(transactions):
    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "balance": round(income - expenses, 2),
    }


def get_category_totals(transactions, type_="expense"):
    totals = {}
    for t in transactions:
        if t["type"] == type_:
            totals[t["category"]] = round(totals.get(t["category"], 0) + t["amount"], 2)
    return totals


def get_monthly_summary(transactions, month):
    """month looks like '2026-10'."""
    in_month = [t for t in transactions if t["date"].startswith(month)]
    return get_summary(in_month)


def get_largest_expense(transactions):
    expenses = [t for t in transactions if t["type"] == "expense"]
    if not expenses:
        return None
    return max(expenses, key=lambda t: t["amount"])