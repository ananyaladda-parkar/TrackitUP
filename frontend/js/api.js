// api.js - the only file that talks to server.py.
// Every function returns:
//   { ok: true, data: ... }                          when the server answered with success
//   { ok: false, unreachable: false, message: "" }   when the backend said no (message comes from your Python code)
//   { ok: false, unreachable: true,  message: "" }   when the server is not running

const Api = (function () {
  async function request(method, url, body) {
    let response;
    try {
      const options = { method: method, headers: {} };
      if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
      }
      response = await fetch(url, options);
    } catch (error) {
      return {
        ok: false,
        unreachable: true,
        message: "Cannot reach the server. Start it with: python server.py"
      };
    }

    let data = null;
    try {
      data = await response.json();
    } catch (error) {
      data = null;
    }

    if (response.ok) {
      return { ok: true, data: data };
    }
    const message = data && data.message ? data.message : "Something went wrong on the server.";
    return { ok: false, unreachable: false, message: message };
  }

  return {
    getTransactions: function () {
      return request("GET", "/api/transactions");
    },
    // fields = { date, type, category, amount, note }  (all text)
    addTransaction: function (fields) {
      return request("POST", "/api/transactions", fields);
    },
    deleteTransaction: function (number) {
      return request("DELETE", "/api/transactions/" + encodeURIComponent(number));
    },
    getSummary: function () {
      return request("GET", "/api/summary");
    },
    getCategoryReport: function () {
      return request("GET", "/api/reports/categories");
    },
    getMonthlyReport: function (month) {
      return request("GET", "/api/reports/monthly?month=" + encodeURIComponent(month));
    },
    getLargestExpense: function () {
      return request("GET", "/api/reports/largest-expense");
    }
  };
})();