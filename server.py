# server.py - lets the browser talk to your existing modules.
# It does NOT change menu.py, validator.py, storage.py, transaction_service.py or reports.py.
# Run:   python server.py
# Open:  http://127.0.0.1:8000

import json
import os
import sys
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

import transaction_service as service

HOST = "127.0.0.1"
DEFAULT_PORT = 8000
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
MAX_BODY_SIZE = 20000
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}

# only one request may touch transactions.csv at a time
backend_lock = threading.Lock()


def text_value(data, key):
    # your service functions call .strip(), so every value must be text
    value = data.get(key, "")
    if value is None:
        return ""
    return str(value)


def numbered(transactions):
    # adds the same 1-based number that the terminal list shows
    result = []
    for position, t in enumerate(transactions, start=1):
        row = dict(t)
        row["number"] = position
        result.append(row)
    return result


def message_reply(ok, message, success_status=200):
    if ok:
        return success_status, {"ok": True, "message": message}
    return 400, {"ok": False, "message": message}


def call_api(method, path, query, data):
    # returns (status code, dictionary to send back as JSON)
    parts = [p for p in path.split("/") if p]
    resource = parts[1:]  # parts[0] is "api"

    if resource == ["transactions"]:
        if method == "GET":
            return 200, {"transactions": numbered(service.get_all_transactions())}
        if method == "POST":
            if not isinstance(data, dict):
                return 400, {"ok": False, "message": "Request body must be a JSON object."}
            ok, message = service.add_transaction(
                text_value(data, "date"),
                text_value(data, "type"),
                text_value(data, "category"),
                text_value(data, "amount"),
                text_value(data, "note"),
            )
            return message_reply(ok, message, 201)

    elif len(resource) == 2 and resource[0] == "transactions":
        if method == "DELETE":
            ok, message = service.delete_transaction(unquote(resource[1]))
            return message_reply(ok, message)

    elif resource == ["summary"]:
        if method == "GET":
            return 200, service.summary()

    elif resource == ["reports", "categories"]:
        if method == "GET":
            return 200, service.category_report()

    elif resource == ["reports", "monthly"]:
        if method == "GET":
            month = query.get("month", [""])[0]
            ok, result = service.monthly_report(month)
            if ok:
                return 200, {"ok": True, "month": month.strip(), "summary": result}
            return 400, {"ok": False, "message": result}

    elif resource == ["reports", "largest-expense"]:
        if method == "GET":
            return 200, {"largest_expense": service.largest_expense()}

    else:
        return 404, {"ok": False, "message": "Not found."}

    return 405, {"ok": False, "message": "This address does not allow " + method + "."}


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_bytes(status, "application/json; charset=utf-8", body)

    def read_json_body(self):
        # returns (data, error message)
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None, "Invalid request."
        if length > MAX_BODY_SIZE:
            return None, "Request is too large."
        if length == 0:
            return {}, None
        try:
            return json.loads(self.rfile.read(length).decode("utf-8")), None
        except (ValueError, UnicodeDecodeError):
            return None, "Request body must be valid JSON."

    def serve_static(self, path):
        if path == "/":
            path = "/index.html"
        root = os.path.realpath(FRONTEND_FOLDER)
        full = os.path.realpath(os.path.join(root, unquote(path).lstrip("/")))
        extension = os.path.splitext(full)[1].lower()
        if not full.startswith(root + os.sep) or not os.path.isfile(full) or extension not in CONTENT_TYPES:
            self.send_json(404, {"ok": False, "message": "Not found."})
            return
        with open(full, "rb") as file:
            self.send_bytes(200, CONTENT_TYPES[extension], file.read())

    def handle_request(self, method):
        url = urlparse(self.path)
        if url.path == "/api" or url.path.startswith("/api/"):
            data = None
            if method == "POST":
                data, error = self.read_json_body()
                if error:
                    self.send_json(400, {"ok": False, "message": error})
                    return
            try:
                with backend_lock:
                    status, payload = call_api(method, url.path, parse_qs(url.query), data)
            except Exception:
                traceback.print_exc()
                status = 500
                payload = {"ok": False, "message": "Something went wrong on the server. Check the terminal for details."}
            self.send_json(status, payload)
        elif method == "GET":
            self.serve_static(url.path)
        else:
            self.send_json(405, {"ok": False, "message": "Not allowed."})

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_DELETE(self):
        self.handle_request("DELETE")


def main():
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Port must be a number, for example: python server.py 8001")
            return
    try:
        server = ThreadingHTTPServer((HOST, port), Handler)
    except OSError:
        print("Port " + str(port) + " is already in use. Close the other program or run: python server.py 8001")
        return
    server.daemon_threads = True
    print("TrackitUP is running at http://" + HOST + ":" + str(port))
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


main()