"""Personal practice UI. Run inside your private Codespace: python practice_server.py.

Executes your Python with the permissions of your Codespace. Keep port 8000 private.
"""
import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
STATE_DIR = Path(os.environ.get('PRACTICE_STATE_DIR', ROOT / '.practice'))
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = STATE_DIR / 'session.json'
LOCK = threading.RLock()
RUN_LOCK = threading.Lock()
TOKEN = secrets.token_urlsafe(32)
NAMES = [['clean_events'], ['build_features'], ['inactivity_score'],
         ['train_model', 'evaluate_model'], ['prioritize_customers']]
TESTS = ['test_01_clean.py', 'test_02_features.py', 'test_03_numpy.py',
         'test_04_model.py', 'test_05_business.py']
SOURCE = (ROOT / 'assessment/solution.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)
LINES = SOURCE.splitlines(keepends=True)
FIRST = min(n.lineno for n in TREE.body if isinstance(n, ast.FunctionDef))
PREAMBLE = ''.join(LINES[:FIRST - 1])
FUNCTIONS = {n.name: ''.join(LINES[n.lineno - 1:n.end_lineno]) for n in TREE.body if isinstance(n, ast.FunctionDef)}
STARTERS = ['import numpy as np\nimport pandas as pd\n\n' + '\n\n'.join(FUNCTIONS[n] for n in names) + '\n' for names in NAMES]

def read_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {'codes': STARTERS.copy(), 'grades': {}, 'revision': 0}

def write_state(state):
    tmp = STATE_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
    tmp.replace(STATE_FILE)

def save_code(stage, code):
    with LOCK:
        state = read_state()
        if state['codes'][stage] != code:
            state['codes'][stage] = code
            state['grades'] = {k: v for k, v in state['grades'].items() if int(k) < stage}
            state['revision'] += 1
            write_state(state)
        return state

def assemble(codes):
    return PREAMBLE + '\n\n'.join(codes) + '\n'

def fingerprint(codes, stage):
    return hashlib.sha256('\n'.join(codes[:stage + 1]).encode()).hexdigest()

def execute(stage, mode, state):
    # Later unfinished stages never prevent checking an earlier one.
    codes = state['codes'][:stage + 1] + STARTERS[stage + 1:]
    source = assemble(codes)
    try:
        compile(source, 'solution.py', 'exec')
    except SyntaxError as exc:
        return {'ok': False, 'output': f'{exc.__class__.__name__}: {exc.msg}\nLínea {exc.lineno}: {exc.text or ""}', 'kind': mode}
    with tempfile.TemporaryDirectory(prefix='practice-') as temp:
        path = Path(temp)
        shutil.copytree(ROOT / 'tests', path / 'tests', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(ROOT / 'data', path / 'data')
        (path / 'assessment').mkdir()
        (path / 'assessment/__init__.py').write_text('', encoding='utf-8')
        (path / 'assessment/solution.py').write_text(source, encoding='utf-8')
        if mode == 'check':
            args = [sys.executable, '-m', 'pytest', '-v', '--tb=short', '--color=no', '-p', 'no:cacheprovider', 'tests/' + TESTS[stage]]
        else:
            demo = [
                "print(clean_events(pd.read_csv('data/events_history.csv').head(12)).to_string(index=False))",
                "e = clean_events(pd.read_csv('data/events_history.csv'))\nf = build_features(pd.read_csv('data/customers_history.csv'), e)\nprint(f.head(8).to_string(index=False))",
                "f = pd.DataFrame({'sessions':[0,1,9], 'active_days':[0,15,30], 'support_tickets':[0,5,10]})\nprint(inactivity_score(f))",
                "e = clean_events(pd.read_csv('data/events_history.csv'))\nf = build_features(pd.read_csv('data/customers_history.csv'), e)\nf['inactivity_score'] = inactivity_score(f)\nm, X, y = train_model(f)\nprint(evaluate_model(m, X, y))",
                "e = clean_events(pd.read_csv('data/events_history.csv'))\nf = build_features(pd.read_csv('data/customers_history.csv'), e)\nf['inactivity_score'] = inactivity_score(f)\nm, X, y = train_model(f)\nlive = build_features(pd.read_csv('data/customers_live.csv'), clean_events(pd.read_csv('data/events_live.csv')))\nlive['inactivity_score'] = inactivity_score(live)\nprint(prioritize_customers(m, live).head(10).to_string(index=False))"
            ][stage]
            (path / 'example.py').write_text('from assessment.solution import *\n' + demo + '\n', encoding='utf-8')
            args = [sys.executable, 'example.py']
        env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', MPLBACKEND='Agg', OPENBLAS_NUM_THREADS='1')
        # A separate process and a timeout keep mistakes from blocking the UI.
        with (path / 'output.txt').open('w+', encoding='utf-8') as log:
            proc = subprocess.Popen(args, cwd=path, stdout=log, stderr=subprocess.STDOUT, env=env,
                                    start_new_session=(os.name != 'nt'))
            timeout = False
            try:
                proc.wait(timeout=40)
            except subprocess.TimeoutExpired:
                timeout = True
                if os.name != 'nt':
                    import signal
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
                proc.wait()
            log.seek(0)
            output = log.read(40000).replace(temp, '<ejercicio>')
        if timeout:
            output += '\nTiempo máximo: 40 segundos. Revisa si hay un bucle infinito.'
        result = {'ok': proc.returncode == 0 and not timeout, 'output': output or 'Ejecutado sin salida.', 'kind': mode}
        if mode == 'check':
            with LOCK:
                current = read_state()
                if fingerprint(current['codes'], stage) == fingerprint(state['codes'], stage):
                    current['grades'][str(stage)] = result['ok']
                    write_state(current)
        return result

class Handler(BaseHTTPRequestHandler):
    def send(self, status, data, content_type='application/json; charset=utf-8'):
        if not isinstance(data, bytes):
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == '/':
            page = (ROOT / 'practice.html').read_text(encoding='utf-8').replace('__SESSION_TOKEN__', TOKEN)
            self.send(200, page.encode(), 'text/html; charset=utf-8')
        elif route == '/api/state':
            with LOCK:
                state = read_state()
            tables = {}
            for name in ['customers_history','events_history','customers_live','events_live']:
                with (ROOT / 'data' / (name + '.csv')).open(encoding='utf-8', newline='') as f:
                    rows = list(csv.reader(f))
                tables[name] = {'columns': rows[0], 'rows': rows[1:9], 'count': len(rows) - 1}
            self.send(200, dict(state, tables=tables, preamble=PREAMBLE))
        elif route == '/download':
            with LOCK:
                source = assemble(read_state()['codes'])
            self.send(200, source.encode(), 'text/x-python; charset=utf-8')
        elif route == '/favicon.ico':
            self.send(204, b'')
        else:
            self.send(404, {'error': 'No encontrado'})

    def do_POST(self):
        if self.headers.get('X-Practice-Token') != TOKEN:
            return self.send(403, {'error': 'Recarga la página para reconectar.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 150000:
                raise ValueError('El código es demasiado largo.')
            body = json.loads(self.rfile.read(size))
            stage = body['stage']
            if type(stage) is not int or not 0 <= stage < 5 or not isinstance(body['code'], str):
                raise ValueError('Etapa no válida.')
            route = urlparse(self.path).path
            if route not in ['/api/save','/api/run','/api/check']:
                return self.send(404, {'error': 'No encontrado'})
            state = save_code(stage, body['code'])
            if route == '/api/save':
                return self.send(200, {'saved': True, 'grades': state['grades']})
            if not RUN_LOCK.acquire(blocking=False):
                return self.send(409, {'error': 'Ya hay una ejecución en curso.'})
            try:
                result = execute(stage, route.split('/')[-1], state)
                with LOCK:
                    result['grades'] = read_state()['grades']
                self.send(200, result)
            finally:
                RUN_LOCK.release()
        except (ValueError, KeyError, TypeError) as exc:
            self.send(400, {'error': str(exc)})
        except Exception as exc:
            self.send(500, {'error': 'No se pudo completar la operación: ' + str(exc)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
    print(f'Practice ready on http://localhost:{port}', flush=True)
    server.serve_forever()
