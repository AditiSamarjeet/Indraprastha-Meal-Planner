"""
Indraprastha Meal Planner — Real-time Sync Server
Serves index.html + syncs data across all devices instantly via SSE.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, threading, queue, socket

ROOT     = os.path.dirname(os.path.abspath(__file__))
INDEX    = os.path.join(ROOT, 'index.html')
DATA_FILE= os.path.join(ROOT, 'data.json')

_subs, _lock = [], threading.Lock()


def _local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80)); ip = s.getsockname()[0]; s.close(); return ip
    except: return 'localhost'


class Handler(BaseHTTPRequestHandler):

    # ── routing ──────────────────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()

    def do_GET(self):
        p = self.path.split('?')[0]
        if p in ('/', '/index.html'):
            self._send_file(INDEX, 'text/html; charset=utf-8')
        elif p == '/sync/data':
            self._send_file(DATA_FILE, 'application/json') if os.path.exists(DATA_FILE) else self._send_text('{}', 'application/json')
        elif p == '/sync/events':
            self._sse()
        else:
            self.send_response(404); self._cors(); self.end_headers()

    def do_POST(self):
        if self.path.split('?')[0] == '/sync/data':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try: json.loads(body)
            except: self.send_response(400); self._cors(); self.end_headers(); return
            with open(DATA_FILE, 'wb') as f: f.write(body)
            with _lock:
                for q in _subs[:]:
                    try: q.put_nowait('update')
                    except: pass
            self.send_response(204); self._cors(); self.end_headers()
        else:
            self.send_response(404); self._cors(); self.end_headers()

    # ── helpers ──────────────────────────────────────────────────
    def _send_file(self, path, ctype):
        with open(path, 'rb') as f: data = f.read()
        self.send_response(200); self._cors()
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers(); self.wfile.write(data)

    def _send_text(self, text, ctype='text/plain'):
        data = text.encode()
        self.send_response(200); self._cors()
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers(); self.wfile.write(data)

    def _sse(self):
        q = queue.Queue()
        with _lock: _subs.append(q)
        self.send_response(200); self._cors()
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Accel-Buffering', 'no')
        self.end_headers()
        try:
            self.wfile.write(b'event: connected\ndata: ok\n\n'); self.wfile.flush()
            while True:
                try:
                    msg = q.get(timeout=20)
                    self.wfile.write(f'event: update\ndata: {msg}\n\n'.encode()); self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b': ping\n\n'); self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError): pass
        finally:
            with _lock:
                if q in _subs: _subs.remove(q)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        if '/sync/events' not in str(args): print(f'  {self.address_string()}  {fmt%args}')


class ThreadedServer(HTTPServer):
    def process_request(self, req, addr):
        t = threading.Thread(target=self._run, args=(req, addr), daemon=True); t.start()
    def _run(self, req, addr):
        try: self.finish_request(req, addr)
        except: pass
        finally: self.shutdown_request(req)


if __name__ == '__main__':
    ip, port = _local_ip(), 8000
    server = ThreadedServer(('0.0.0.0', port), Handler)
    import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout,'reconfigure') else None
    print(f'\n  Indraprastha Sync Server\n')
    print(f'  Laptop : http://localhost:{port}/')
    print(f'  Phone  : http://{ip}:{port}/')
    print(f'\n  Changes on any device sync instantly.')
    print(f'  Press Ctrl+C to stop.\n')
    try: server.serve_forever()
    except KeyboardInterrupt: print('\n  Stopped.')
