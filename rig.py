# -*- coding: utf-8 -*-
"""Thin client for the ai-film-bridge Worker -> Bob's Windows workstation ("the Beast").

Same wiring minimax-h3 uses: POST /api/enqueue with the admin token, poll /api/job/<id>.
The agent runs the `command` as PowerShell on the rig and ships stdout back.

⚠ Cloudflare 403s the default Python-urllib User-Agent (see minimax-h3/driver.py) — send a
browser UA on every call or the token looks fine and the request still dies.
"""
import json
import sys
import time
import urllib.request

CFG = json.load(open('/root/.config/ai-film-bridge.json'))
U = CFG['url'].rstrip('/')
ADMIN = CFG['admin_token']
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/131.0 Safari/537.36')


def _req(path, data=None, timeout=60):
    rq = urllib.request.Request(
        U + path, data=data,
        headers={'content-type': 'application/json', 'x-admin-token': ADMIN, 'User-Agent': UA})
    return json.load(urllib.request.urlopen(rq, timeout=timeout))


def enq(label, cmd, timeout_s=900):
    r = _req('/api/enqueue', json.dumps(
        {"label": label, "command": cmd, "timeout_s": timeout_s}).encode())
    if not r.get('ok'):
        raise SystemExit(f"enqueue failed: {r}")
    return r['id']


def job(jid):
    return _req(f'/api/job/{jid}').get('job', {})


def wait(jid, poll=10, limit=7200, quiet=False):
    """Block until the job leaves the queue. Returns the job dict."""
    t0 = time.time()
    last = None
    while time.time() - t0 < limit:
        j = job(jid)
        st = j.get('status')
        if st != last and not quiet:
            print(f"  [{int(time.time()-t0):5d}s] job {jid} -> {st}", flush=True)
            last = st
        if st in ('done', 'error', 'failed', 'timeout', 'cancelled'):
            return j
        time.sleep(poll)
    return {'status': 'WAIT_TIMEOUT', 'id': jid}


def run(label, cmd, timeout_s=900, poll=10):
    """Enqueue, wait, print stdout. Returns the job dict."""
    jid = enq(label, cmd, timeout_s)
    print(f"queued {label} -> {jid}", flush=True)
    j = wait(jid, poll=poll, limit=timeout_s + 600)
    print(f"--- {label}: {j.get('status')} ---")
    out = j.get('stdout') or j.get('output') or ''
    print(out)
    if j.get('stderr'):
        print("STDERR:", j['stderr'][:2000])
    return j


def agents():
    return _req('/api/agents').get('agents', [])


if __name__ == '__main__':
    if sys.argv[1:] and sys.argv[1] == 'agents':
        for a in agents():
            print(json.dumps(a))
    elif sys.argv[1:] and sys.argv[1] == 'job':
        print(json.dumps(job(sys.argv[2]), indent=2)[:8000])
