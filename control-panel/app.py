from flask import Flask, render_template_string, jsonify
import os
import subprocess

app = Flask(__name__)

USG_HOST = os.getenv('USG_HOST', '192.168.1.1')
USG_USER = os.getenv('USG_USER', 'Comtex')
USG_PASSWORD = os.getenv('USG_PASSWORD', '')

COMMANDS = {
    'network': {'label': 'Network Status', 'cmd': 'show interfaces'},
    'sqm': {'label': 'SQM Status', 'cmd': '/sbin/tc qdisc show dev pppoe0'},
    'pppoe': {'label': 'PPPoE Status', 'cmd': 'show pppoe-client'},
    'system': {'label': 'System Resources', 'cmd': 'show version'}
}

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>UniFi Control Panel</title>
    <style>
        body { background: #0f172a; color: white; font-family: sans-serif; padding: 20px; margin: 0; }
        h1 { color: #60a5fa; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .card { background: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
        .card h3 { color: #60a5fa; margin-top: 0; }
        .btn { background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; width: 100%; }
        .btn:hover { background: #2563eb; }
        .output { background: #0f172a; padding: 20px; border-radius: 8px; border: 1px solid #334155; margin-top: 20px; display: none; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>🔧 UniFi Control Panel</h1>
    <div class="grid">
        {% for key, cmd in commands.items() %}
        <div class="card">
            <h3>{{ cmd.label }}</h3>
            <button class="btn" onclick="runCmd('{{ key }}')">Execute</button>
        </div>
        {% endfor %}
    </div>
    <pre id="output" class="output"></pre>
    <script>
        async function runCmd(k) {
            document.getElementById('output').style.display = 'block';
            document.getElementById('output').textContent = 'Loading...';
            const r = await fetch('/api/' + k);
            const d = await r.json();
            document.getElementById('output').textContent = d.output || d.error || 'No output';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML, commands=COMMANDS)

@app.route('/api/<cmd>')
def api(cmd):
    if cmd not in COMMANDS:
        return jsonify({'error': 'Unknown command'}), 404
    if not USG_PASSWORD:
        return jsonify({'output': 'Error: Password not configured'})
    try:
        ssh = ['sshpass', '-p', USG_PASSWORD, 'ssh', '-o', 'StrictHostKeyChecking=no', 
               '-o', 'ConnectTimeout=10', f'{USG_USER}@{USG_HOST}', COMMANDS[cmd]['cmd']]
        r = subprocess.run(ssh, capture_output=True, text=True, timeout=30)
        return jsonify({'output': r.stdout + (r.stderr if r.stderr else '')})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
