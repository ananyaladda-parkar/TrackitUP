# TrackitUP

TrackitUP is a personal income and expense tracker. It has a browser-based frontend and a small Python HTTP server that connects the frontend to the transaction and reporting code. Transaction data is saved locally in `transactions.csv`.

## Requirements

- Windows 10 or later
- Python 3.8 or later
- A modern web browser

The web app uses only Python's standard library. There are no packages to install and no separate frontend build step.

## Set up

### 1. Get the project

If you have not already downloaded the project, open PowerShell and clone it:

```powershell
git clone https://github.com/ananyaladda-parkar/TrackitUP.git
cd TrackitUP
```

If you already have the project folder, open PowerShell and change to that folder instead. For example:

```powershell
cd "C:\Users\YourName\OneDrive - Parkar\Desktop\TrackitUP"
```

Replace the example path with the location of your project. You can also open the project folder in VS Code, then choose **Terminal > New Terminal**; the terminal will usually start in the project folder.

### 2. Install Python if needed

In PowerShell, check whether Python is available:

```powershell
python --version
```

If Windows cannot find `python`, install Python 3 from [python.org](https://www.python.org/downloads/windows/). During installation, select **Add Python to PATH**. Close and reopen PowerShell after installing, then check the version again. On some Windows setups, the Python launcher works instead:

```powershell
py --version
```

### 3. Start the application

Make sure PowerShell is in the project folder (the folder containing `server.py`), then run:

```powershell
python server.py
```

If your system uses the Python launcher, run:

```powershell
py server.py
```

The terminal should show that TrackitUP is running at `http://127.0.0.1:8000`. Keep this terminal open while using the app; it is running the local web server.

### 4. Open the frontend

Open this address in your browser:

<http://127.0.0.1:8000>

The server provides both the frontend files and the API used by the frontend. Start the app with `server.py` rather than opening `frontend\index.html` directly; the browser needs the server for transactions and reports.

## Use the application

Use the navigation at the top of the page:

- **Overview** shows your income, expenses, balance, largest expense, and recent entries.
- **Transactions** lists saved transactions. The displayed number is the row's current position; deleting a transaction renumbers the rows below it.
- **Add** lets you enter a date, income or expense type, category, amount, and optional note. Dates must not be in the future, and amounts must be greater than zero.
- **Reports** shows totals by category and a summary for a month entered as `YYYY-MM` (for example, `2026-10`).

Data is stored in `transactions.csv` in the project folder. The file is created when the first transaction is saved. Keep a copy of this file if you want to back up your transactions. Do not edit it in another program while TrackitUP is saving data.

## Stop the application

When you are finished, switch to the PowerShell terminal running the server and press **Ctrl+C**. You can close the browser tab separately.

## Troubleshooting

### `python` is not recognized

Try `py server.py`. If that also fails, install Python and enable **Add Python to PATH**, then reopen the terminal.

### Port 8000 is already in use

Start the app on another port:

```powershell
python server.py 8001
```

Then open <http://127.0.0.1:8001>. Use the same port number in the browser that you supplied to `server.py`.

### The page says it cannot reach the server

Confirm that the server terminal is still running and that you opened the matching `127.0.0.1` address and port. If the server has stopped, start it again with `python server.py`.

### The app cannot save a transaction

Check that the project folder is writable. If `transactions.csv` is open in Excel or another program, close it and try again.

## Project files

| File or folder | Purpose |
| --- | --- |
| `server.py` | Starts the local web server, serves the frontend, and handles API requests. |
| `frontend\index.html` | Defines the browser app's pages and forms. |
| `frontend\css\styles.css` | Styles the browser app. |
| `frontend\js\api.js` | Sends requests from the frontend to the Python API. |
| `frontend\js\app.js` | Controls frontend navigation, rendering, and form behavior. |
| `transaction_services.py` | Validates and processes transaction and report requests. |
| `validator.py` | Checks transaction fields and month formats. |
| `storage.py` | Reads and writes `transactions.csv`. |
| `reports.py` | Calculates balances, category totals, monthly summaries, and the largest expense. |
| `transactions.csv` | Local transaction data, created when the first transaction is saved. |
