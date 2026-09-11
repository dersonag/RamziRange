#!/usr/bin/env python3
"""
internal-admin — a mock internal service with NO host port (reachable only from
inside the Docker network, e.g. via the main app's SSRF). Part of RamziRange8's
multi-hop chain: SSRF -> internal service -> leaked creds -> lateral movement.
Deliberately insecure; lab use only.
"""
import subprocess
from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def index():
    return ("internal-admin (not internet-facing)\n"
            "endpoints: /creds  /exec?cmd=  /latest/meta-data/\n")


@app.route("/creds")
def creds():
    # Internal secrets — the payoff of an SSRF pivot; also the lateral-movement cred.
    return ("# internal service account registry\n"
            "SSH_DEPLOY_USER=svc_deploy\n"
            "SSH_DEPLOY_PASSWORD=D3pl0y!R3l3ase2026\n"
            "REDIS_PASSWORD=r3d1s-internal-2026\n"
            "FLAG=RR8{ssrf_reached_internal_admin}\n")


@app.route("/latest/meta-data/")
def metadata():
    return "iam/  hostname\ninstance-id: i-0ffee1nternal\n"


@app.route("/exec")
def exec_cmd():
    # Internal RCE — if the SSRF can drive this, it's a second host-compromise hop.
    cmd = request.args.get("cmd", "")
    if not cmd:
        return "usage: /exec?cmd=<command>\n"
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10).stdout
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
