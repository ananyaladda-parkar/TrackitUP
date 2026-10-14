// app.js - draws the pages and handles clicks.
// All numbers and messages come from your Python code through api.js.

(function () {
  "use strict";

  const ROUTES = ["overview", "transactions", "add", "reports"];
  const TITLES = {
    overview: "Overview",
    transactions: "Transactions",
    add: "Add a transaction",
    reports: "Reports"
  };

  // ---------- small helpers ----------

  function byId(id) {
    return document.getElementById(id);
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (text !== undefined) {
      node.textContent = text;
    }
    return node;
  }

  function clear(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  const moneyFormat = new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });

  function formatMoney(value) {
    return moneyFormat.format(value);
  }

  function signedMoney(transaction) {
    const sign = transaction.type === "income" ? "+" : "\u2212";
    return sign + formatMoney(transaction.amount);
  }

  function typeLabel(type) {
    return type === "income" ? "Income" : "Expense";
  }

  function todayText() {
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    return now.getFullYear() + "-" + month + "-" + day;
  }

  // ---------- notice bar ----------

  const noticeBox = byId("notice");

  function showNotice(message, kind) {
    noticeBox.textContent = message;
    noticeBox.className = "notice notice-" + kind;
    noticeBox.hidden = false;
  }

  function hideNotice() {
    noticeBox.hidden = true;
    noticeBox.textContent = "";
  }

  // returns true if every result worked, otherwise shows the problem and returns false
  function allOk(results) {
    for (let i = 0; i < results.length; i++) {
      if (!results[i].ok) {
        showNotice(results[i].message, "error");
        return false;
      }
    }
    return true;
  }

  // ---------- overview ----------

  async function loadOverview() {
    const results = await Promise.all([
      Api.getSummary(),
      Api.getLargestExpense(),
      Api.getTransactions()
    ]);
    if (!allOk(results)) {
      return;
    }
    const summary = results[0].data;
    const largest = results[1].data.largest_expense;
    const transactions = results[2].data.transactions;

    // balance
    byId("figure-balance").textContent = formatMoney(summary.balance);
    byId("figure-income").textContent = formatMoney(summary.income);
    byId("figure-expenses").textContent = formatMoney(summary.expenses);
    const negative = summary.balance < 0;
    byId("figure-balance-box").classList.toggle("is-negative", negative);
    byId("balance-note").textContent = negative
      ? "You have spent more than you earned."
      : "Income minus expenses.";

    // income / expense bar
    const total = summary.income + summary.expenses;
    const incomePart = total > 0 ? (summary.income / total) * 100 : 0;
    const expensePart = total > 0 ? (summary.expenses / total) * 100 : 0;
    byId("split-income").style.width = incomePart + "%";
    byId("split-expense").style.width = expensePart + "%";
    byId("split-bar").setAttribute(
      "aria-label",
      total > 0
        ? "Income " + formatMoney(summary.income) + ", expenses " + formatMoney(summary.expenses)
        : "No income or expenses yet"
    );

    // largest expense
    const largestBox = byId("largest-expense");
    clear(largestBox);
    if (largest === null) {
      largestBox.appendChild(el("p", "muted", "No expenses yet."));
    } else {
      largestBox.appendChild(el("p", "largest-amount", formatMoney(largest.amount)));
      largestBox.appendChild(el("p", "largest-category", largest.category));
      let detail = largest.date;
      if (largest.note) {
        detail = detail + " \u2013 " + largest.note;
      }
      largestBox.appendChild(el("p", "muted", detail));
    }

    // latest entries (last 5 rows in the file, newest first)
    const list = byId("recent-list");
    clear(list);
    if (transactions.length === 0) {
      list.appendChild(el("li", "muted", "Nothing added yet."));
    } else {
      const latest = transactions.slice(-5).reverse();
      latest.forEach(function (t) {
        const item = el("li", "ledger-row");
        item.appendChild(el("span", "ledger-date", t.date));
        const middle = el("span", "ledger-main");
        middle.appendChild(el("span", "category", t.category));
        if (t.note) {
          middle.appendChild(el("span", "muted note-line", t.note));
        }
        item.appendChild(middle);
        item.appendChild(el("span", "amount amount-" + t.type, signedMoney(t)));
        list.appendChild(item);
      });
    }
  }

  // ---------- transactions ----------

  function sameTransaction(a, b) {
    return (
      a.date === b.date &&
      a.type === b.type &&
      a.category === b.category &&
      a.amount === b.amount &&
      a.note === b.note
    );
  }

  async function deleteRow(transaction) {
    // the backend deletes by position, so first check the row is still where we think it is
    const fresh = await Api.getTransactions();
    if (!allOk([fresh])) {
      return;
    }
    const rows = fresh.data.transactions;
    const current = rows[transaction.number - 1];
    if (!current || !sameTransaction(current, transaction)) {
      showNotice("The list changed since it was loaded, so nothing was deleted. The list has been reloaded.", "error");
      renderTransactions(rows);
      return;
    }
    const result = await Api.deleteTransaction(transaction.number);
    if (result.ok) {
      showNotice(result.data.message, "success");
    } else {
      showNotice(result.message, "error");
    }
    loadTransactions();
  }

  function makeDeleteButton(transaction) {
    const button = el("button", "btn-delete", "Delete");
    button.type = "button";
    button.setAttribute("aria-label", "Delete transaction " + transaction.number);
    let timer = null;

    function disarm() {
      button.classList.remove("armed");
      button.textContent = "Delete";
      button.setAttribute("aria-label", "Delete transaction " + transaction.number);
    }

    button.addEventListener("click", function () {
      if (!button.classList.contains("armed")) {
        button.classList.add("armed");
        button.textContent = "Confirm delete";
        button.setAttribute("aria-label", "Confirm delete of transaction " + transaction.number);
        timer = setTimeout(disarm, 4000);
        return;
      }
      clearTimeout(timer);
      button.disabled = true;
      deleteRow(transaction);
    });
    return button;
  }

  function addCell(row, label, content, className) {
    const cell = el("td", className || "");
    cell.setAttribute("data-label", label);
    if (typeof content === "string") {
      cell.textContent = content;
    } else {
      cell.appendChild(content);
    }
    row.appendChild(cell);
  }

  function renderTransactions(transactions) {
    const body = byId("transactions-body");
    clear(body);
    const isEmpty = transactions.length === 0;
    byId("transactions-empty").hidden = !isEmpty;
    byId("transactions-table").hidden = isEmpty;

    transactions.forEach(function (t) {
      const row = el("tr");
      addCell(row, "No.", String(t.number), "col-number");
      addCell(row, "Date", t.date, "col-date");
      addCell(row, "Type", el("span", "tag tag-" + t.type, typeLabel(t.type)), "col-type");
      addCell(row, "Category", t.category, "col-category");
      addCell(row, "Note", t.note || "", "col-note");
      addCell(row, "Amount", signedMoney(t), "num amount amount-" + t.type);
      addCell(row, "", makeDeleteButton(t), "col-action");
      body.appendChild(row);
    });
  }

  async function loadTransactions() {
    const result = await Api.getTransactions();
    if (!allOk([result])) {
      return;
    }
    renderTransactions(result.data.transactions);
  }

  // ---------- add ----------

  function prepareAddForm() {
    const dateInput = byId("add-date");
    if (!dateInput.value) {
      dateInput.value = todayText();
    }
    byId("add-result").hidden = true;
  }

  function showAddResult(message, kind) {
    const box = byId("add-result");
    box.textContent = message;
    box.className = "form-result form-result-" + kind;
    box.hidden = false;
  }

  byId("add-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    const button = byId("add-submit");
    button.disabled = true;

    const result = await Api.addTransaction({
      date: byId("add-date").value,
      type: byId("add-type").value,
      category: byId("add-category").value,
      amount: byId("add-amount").value,
      note: byId("add-note").value
    });

    button.disabled = false;
    if (result.ok) {
      showAddResult(result.data.message, "success");
      byId("add-category").value = "";
      byId("add-amount").value = "";
      byId("add-note").value = "";
      byId("add-category").focus();
    } else {
      showAddResult(result.message, "error");
    }
  });

  // ---------- reports ----------

  function renderCategoryTotals(container, totals, kind, emptyText) {
    clear(container);
    const names = Object.keys(totals).sort(function (a, b) {
      return totals[b] - totals[a];
    });
    if (names.length === 0) {
      container.appendChild(el("p", "muted", emptyText));
      return;
    }
    const biggest = totals[names[0]];
    names.forEach(function (name) {
      const row = el("div", "cat-row");
      const top = el("div", "cat-top");
      top.appendChild(el("span", "category", name));
      top.appendChild(el("span", "amount", formatMoney(totals[name])));
      row.appendChild(top);
      const track = el("div", "cat-track");
      const fill = el("div", "cat-fill cat-fill-" + kind);
      fill.style.width = (totals[name] / biggest) * 100 + "%";
      track.appendChild(fill);
      row.appendChild(track);
      container.appendChild(row);
    });
  }

  async function loadReports() {
    const result = await Api.getCategoryReport();
    if (!allOk([result])) {
      return;
    }
    renderCategoryTotals(byId("category-expense"), result.data.expense, "expense", "No expenses yet.");
    renderCategoryTotals(byId("category-income"), result.data.income, "income", "No income yet.");
    const monthInput = byId("month-input");
    if (!monthInput.value) {
      monthInput.value = todayText().slice(0, 7);
    }
  }

  function monthFigure(label, value, className) {
    const box = el("div", "month-figure");
    box.appendChild(el("dt", "", label));
    box.appendChild(el("dd", className || "", formatMoney(value)));
    return box;
  }

  byId("month-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    const errorBox = byId("month-error");
    const resultBox = byId("month-result");
    errorBox.hidden = true;
    clear(resultBox);

    const result = await Api.getMonthlyReport(byId("month-input").value);
    if (!result.ok) {
      errorBox.textContent = result.message;
      errorBox.hidden = false;
      return;
    }
    const summary = result.data.summary;
    resultBox.appendChild(el("h3", "", result.data.month));
    if (summary.income === 0 && summary.expenses === 0) {
      resultBox.appendChild(el("p", "muted", "No transactions in this month."));
      return;
    }
    const list = el("dl", "month-figures");
    list.appendChild(monthFigure("Income", summary.income, "amount-income"));
    list.appendChild(monthFigure("Expenses", summary.expenses, "amount-expense"));
    list.appendChild(monthFigure("Balance", summary.balance, summary.balance < 0 ? "amount-negative" : ""));
    resultBox.appendChild(list);
  });

  // ---------- routing ----------

  const loaders = {
    overview: loadOverview,
    transactions: loadTransactions,
    add: prepareAddForm,
    reports: loadReports
  };

  function currentRoute() {
    const name = window.location.hash.replace("#/", "");
    return ROUTES.indexOf(name) >= 0 ? name : "overview";
  }

  function showRoute(moveFocus) {
    const name = currentRoute();
    ROUTES.forEach(function (route) {
      byId("view-" + route).hidden = route !== name;
    });
    document.querySelectorAll("nav a").forEach(function (link) {
      if (link.getAttribute("data-route") === name) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
    document.title = TITLES[name] + " - TrackitUP";
    hideNotice();
    loaders[name]();
    if (moveFocus) {
      byId("title-" + name).focus();
    }
  }

  window.addEventListener("hashchange", function () {
    showRoute(true);
  });
  showRoute(false);
})();