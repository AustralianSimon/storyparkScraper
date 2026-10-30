import json, queue, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Storypark Scraper - Login Assist</title>
<style>
  body { font-family: sans-serif; margin: 16px; background: #f4f4f4; }
  #screen { border: 1px solid #888; max-width: 100%; cursor: crosshair; display: block; }
  .controls { margin: 12px 0; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  input[type=text] { padding: 6px; font-size: 16px; width: 240px; }
  button { padding: 6px 12px; font-size: 14px; }
  #status { color: #333; margin-bottom: 8px; }
</style>
</head>
<body>
<h2>Storypark login needs your help</h2>
<p>Complete the captcha / MFA below. Click on the screenshot to click in the browser,
use the text box to type (e.g. your MFA code). The scraper continues automatically once logged in.</p>
<div id="status">Connecting...</div>
<div class="controls">
  <input type="text" id="text" placeholder="Text / MFA code" autocomplete="one-time-code">
  <button onclick="sendText()">Type</button>
  <button onclick="sendKey('Enter')">Enter</button>
  <button onclick="sendKey('Tab')">Tab</button>
  <button onclick="sendKey('Backspace')">Backspace</button>
  <button onclick="post('/done', {})" title="Use if login finished but the scraper has not continued">I'm logged in - continue</button>
</div>
<img id="screen" alt="browser screenshot">
<script>
  const img = document.getElementById('screen');
  function post(path, body) {
    return fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
  }
  function sendKey(key) { post('/key', {key: key}); }
  function sendText() {
    const t = document.getElementById('text');
    post('/type', {text: t.value});
    t.value = '';
  }
  document.getElementById('text').addEventListener('keydown', e => {
    if (e.key === 'Enter') { sendText(); setTimeout(() => sendKey('Enter'), 200); }
  });
  img.addEventListener('click', e => {
    const r = img.getBoundingClientRect();
    const x = (e.clientX - r.left) * img.naturalWidth / r.width;
    const y = (e.clientY - r.top) * img.naturalHeight / r.height;
    post('/click', {x: x, y: y});
  });
  function refresh() {
    const next = new Image();
    next.onload = () => { img.src = next.src; setTimeout(refresh, 700); };
    next.onerror = () => setTimeout(refresh, 1500);
    next.src = '/screenshot.jpg?t=' + Date.now();
  }
  function status() {
    fetch('/status').then(r => r.json()).then(s => {
      document.getElementById('status').textContent = s.done ? 'Logged in - you can close this page.' : 'Current page: ' + s.url;
      if (!s.done) setTimeout(status, 1500);
    }).catch(() => { document.getElementById('status').textContent = 'Scraper is no longer waiting - you can close this page.'; });
  }
  refresh();
  status();
</script>
</body>
</html>
"""


class _State:
    def __init__(self):
        self.lock = threading.Lock()
        self.screenshot = b''
        self.url = ''
        self.done = False
        self.actions = queue.Queue()


def _make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _send(self, code, body, content_type):
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split('?')[0]
            if path == '/':
                self._send(200, PAGE_HTML.encode('utf-8'), 'text/html; charset=utf-8')
            elif path == '/screenshot.jpg':
                with state.lock:
                    shot = state.screenshot
                if shot:
                    self._send(200, shot, 'image/jpeg')
                else:
                    self._send(503, b'', 'text/plain')
            elif path == '/status':
                with state.lock:
                    body = json.dumps({'url': state.url, 'done': state.done})
                self._send(200, body.encode('utf-8'), 'application/json')
            else:
                self._send(404, b'', 'text/plain')

        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            try:
                data = json.loads(self.rfile.read(length) or b'{}')
            except ValueError:
                self._send(400, b'', 'text/plain')
                return
            path = self.path.split('?')[0]
            if path in ('/click', '/type', '/key', '/done'):
                state.actions.put((path[1:], data))
                self._send(204, b'', 'text/plain')
            else:
                self._send(404, b'', 'text/plain')

    return Handler


def _perform(page, action, data):
    if action == 'click':
        page.mouse.click(float(data['x']), float(data['y']))
    elif action == 'type':
        page.keyboard.type(str(data.get('text', '')), delay=50)
    elif action == 'key':
        page.keyboard.press(str(data['key']))


def wait_for_user(page, is_done, host='0.0.0.0', port=8000, timeout=600):
    """
    Starts a small web page showing live screenshots of the browser so the user can
    solve a captcha / enter an MFA code. Clicks and typing are forwarded to the page.
    Playwright objects are only touched from this (the calling) thread.
    Returns when is_done(page) is True or the user presses continue, raises TimeoutError otherwise.
    """
    state = _State()
    server = ThreadingHTTPServer((host, port), _make_handler(state))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print('=' * 60)
    print('Login needs manual input (captcha and/or MFA).')
    print(f'Open http://localhost:{port} in your browser to complete it.')
    print(f'Waiting up to {timeout} seconds...')
    print('=' * 60)

    deadline = time.time() + timeout
    try:
        while True:
            user_done = False
            while not state.actions.empty():
                action, data = state.actions.get()
                if action == 'done':
                    user_done = True
                    continue
                try:
                    _perform(page, action, data)
                except Exception as e:
                    print(f'Login assist action {action} failed: {e}')

            try:
                if user_done or is_done(page):
                    break
                shot = page.screenshot(type='jpeg', quality=70)
                with state.lock:
                    state.screenshot = shot
                    state.url = page.url
            except Exception:
                # Page is likely mid-navigation, try again next loop
                pass

            if time.time() > deadline:
                raise TimeoutError('Timed out waiting for manual login')
            page.wait_for_timeout(500)

        with state.lock:
            state.done = True
        print('Manual login step complete.')
        # Give the open web page a moment to show the logged in status
        time.sleep(2)
    finally:
        server.shutdown()
        server.server_close()
