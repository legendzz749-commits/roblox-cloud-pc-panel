"""
UI server — serves the holographic interface and bridges it to JARVIS.
No extra dependencies: uses Python's built-in http.server.

Run with:  python main.py --ui
Then open: http://localhost:8765
"""
import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

UI_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "interface.html")

# Shared state the main loop updates
STATE = {
    "state": "idle",          # idle | listening | thinking | speaking
    "status_text": "SYSTEMS ONLINE",
    "transcript": "",
    "cpu": None,
    "mem": None,
    "latency": 12,
}

# Set by main.py — callable that takes a command string, returns response string
COMMAND_HANDLER = None


def set_state(state=None, status_text=None, transcript=None):
    if state is not None:
        STATE["state"] = state
    if status_text is not None:
        STATE["status_text"] = status_text
    if transcript is not None:
        STATE["transcript"] = transcript
    try:
        import psutil
        STATE["cpu"] = round(psutil.cpu_percent())
        STATE["mem"] = round(psutil.virtual_memory().percent)
    except ImportError:
        pass


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # silence request logging

    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(UI_PATH, "rb") as f:
                self._send(200, f.read(), "text/html")
        elif self.path == "/state":
            self._send(200, json.dumps(STATE))
        else:
            self._send(404, '{"error":"not found"}')

    def do_POST(self):
        if self.path == "/command":
            length = int(self.headers.get("Content-Length", 0))
            try:
                payload = json.loads(self.rfile.read(length))
                command = payload.get("command", "")
            except json.JSONDecodeError:
                self._send(400, '{"error":"bad json"}')
                return

            if COMMAND_HANDLER is None:
                self._send(200, json.dumps({"response": "Command handler not connected."}))
                return

            set_state(state="thinking", transcript=command)
            response = COMMAND_HANDLER(command)
            set_state(state="idle", transcript=response)
            self._send(200, json.dumps({"response": response}))
        else:
            self._send(404, '{"error":"not found"}')


def start_ui_server(port=8765):
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[ui] Neural interface running at http://localhost:{port}")
    return server
