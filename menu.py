# Member 1 - Menu
# This file only talks to transaction_service. All input() and print() are here.

import transaction_service as service


def show_menu():
    print()
    print("===== Personal Expense Tracker =====")
    print("1. Add transaction")
    print("2. View transactions")
    print("3. Delete transaction")
    print("4. Summary")
    print("5. Category report")
    print("6. Monthly report")
    print("7. Largest expense")
    print("8. Exit")


def show_transactions(transactions):
    if len(transactions) == 0:
        print("No transactions yet.")
        return
    print("No. | Date | Type | Category | Amount | Note")
    number = 1
    for t in transactions:
        print(number, "|", t["date"], "|", t["type"], "|", t["category"], "|", f"{t['amount']:.2f}", "|", t["note"])
        number = number + 1


def show_summary(data):
    print("Total income  :", f"{data['income']:.2f}")
    print("Total expenses:", f"{data['expenses']:.2f}")
    print("Balance       :", f"{data['balance']:.2f}")


def add_screen():
    date = input("Date (YYYY-MM-DD): ")
    type_ = input("Type (income/expense): ")
    category = input("Category: ")
    amount = input("Amount: ")
    note = input("Note (optional): ")
    ok, message = service.add_transaction(date, type_, category, amount, note)
    if ok:
        print(message)
    else:
        print("Error:", message)


def view_screen():
    show_transactions(service.get_all_transactions())


def delete_screen():
    transactions = service.get_all_transactions()
    show_transactions(transactions)
    if len(transactions) == 0:
        return
    number = input("Enter the number to delete: ")
    ok, message = service.delete_transaction(number)
    if ok:
        print(message)
    else:
        print("Error:", message)


def summary_screen():
    show_summary(service.summary())


def category_screen():
    report = service.category_report()

    print("--- Expenses by category ---")
    if len(report["expense"]) == 0:
        print("None")
    for category in report["expense"]:
        print(category, ":", f"{report['expense'][category]:.2f}")

    print("--- Income by category ---")
    if len(report["income"]) == 0:
        print("None")
    for category in report["income"]:
        print(category, ":", f"{report['income'][category]:.2f}")


def monthly_screen():
    month = input("Month (YYYY-MM): ")
    ok, result = service.monthly_report(month)
    if not ok:
        print("Error:", result)
        return
    print("--- Summary for", month.strip(), "---")
    show_summary(result)


def largest_screen():
    t = service.largest_expense()
    if t is None:
        print("No expenses yet.")
    else:
        print("Largest expense:", f"{t['amount']:.2f}", "on", t["category"], "(" + t["date"] + ")", t["note"])


def run():
    while True:
        show_menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_screen()
        elif choice == "2":
            view_screen()
        elif choice == "3":
            delete_screen()
        elif choice == "4":
            summary_screen()
        elif choice == "5":
            category_screen()
        elif choice == "6":
            monthly_screen()
        elif choice == "7":
            largest_screen()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Enter a number from 1 to 8.")



