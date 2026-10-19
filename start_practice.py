"""Start the personal practice UI in the background when the Codespace starts."""
from pathlib import Path
import os
import socket
import subprocess
import sys

root = Path(__file__).resolve().parent
port = int(os.environ.get('PORT', '8000'))
with socket.socket() as sock:
    already_running = sock.connect_ex(('127.0.0.1', port)) == 0
if already_running:
    print(f'Practice is already running on port {port}.')
else:
    (root / '.practice').mkdir(exist_ok=True)
    with (root / '.practice/server.log').open('a', encoding='utf-8') as log:
        subprocess.Popen([sys.executable, str(root / 'practice_server.py')], cwd=root,
                         stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                         start_new_session=True)
    print(f'Practice started on port {port}.')
