import csv
import os

# the csv file is saved in the same folder as this code
FILE_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transactions.csv")
FIELDS = ["date", "type", "category", "amount", "note"]


def load_transactions():
    transactions = []
    if not os.path.exists(FILE_NAME):
        return transactions

    with open(FILE_NAME, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                transaction = {
                    "date": row["date"],
                    "type": row["type"],
                    "category": row["category"],
                    "amount": float(row["amount"]),
                    "note": row["note"] or "",
                }
                transactions.append(transaction)
            except (KeyError, ValueError, TypeError):
                pass  # skip a broken row instead of crashing
    return transactions


def save_transactions(transactions):
    # returns True if saved, False if the file could not be written
    try:
        with open(FILE_NAME, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            for transaction in transactions:
                writer.writerow(transaction)
        return True
    except OSError:
        return False