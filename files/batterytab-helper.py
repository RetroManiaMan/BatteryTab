#!/usr/bin/env python3
"""BatteryTab helper.

Firefox and Safari don't let websites read your battery, so this tiny script reads it
from your operating system and serves it on http://127.0.0.1:8765/battery. Keep it
running and BatteryTab will pick it up automatically. Works on macOS, Linux and Windows
with nothing to install (Python 3 standard library only).

    python3 batterytab-helper.py                      # start
    python3 batterytab-helper.py --origin https://you.github.io   # only allow your site
    python3 batterytab-helper.py --fake 72            # fake data, for testing
"""
import argparse, glob, json, platform, re, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def read_mac():
    out = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, timeout=5).stdout
    m = re.search(r"(\d+)%", out)
    if not m:
        return None
    plugged = "AC Power" in out.splitlines()[0]
    t = re.search(r"(\d+):(\d+) remaining", out)
    secs = int(t.group(1)) * 3600 + int(t.group(2)) * 60 if t and (int(t.group(1)) or int(t.group(2))) else None
    return {"level": int(m.group(1)), "charging": plugged,
            "chargingTime": secs if plugged else None, "dischargingTime": None if plugged else secs}


def _num(path):
    try:
        return float(open(path).read().strip())
    except Exception:
        return None


def read_linux():
    for d in sorted(glob.glob("/sys/class/power_supply/BAT*")):
        cap = _num(d + "/capacity")
        if cap is None:
            continue
        status = open(d + "/status").read().strip().lower() if glob.glob(d + "/status") else ""
        plugged = status != "discharging"
        now = _num(d + "/energy_now") or _num(d + "/charge_now")
        full = _num(d + "/energy_full") or _num(d + "/charge_full")
        rate = _num(d + "/power_now") or _num(d + "/current_now")
        secs = None
        if now and rate and rate > 0:
            secs = int(((full - now) if status == "charging" else now) / rate * 3600)
        return {"level": int(cap), "charging": plugged,
                "chargingTime": secs if status == "charging" else None,
                "dischargingTime": secs if status == "discharging" else None}
    return None


def read_windows():
    cmd = "Get-CimInstance Win32_Battery | Select-Object EstimatedChargeRemaining,BatteryStatus,EstimatedRunTime | ConvertTo-Json"
    out = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=10).stdout
    if not out.strip():
        return None
    d = json.loads(out)
    d = d[0] if isinstance(d, list) else d
    plugged = d.get("BatteryStatus") in (2, 3, 6, 7, 8, 9)
    run = d.get("EstimatedRunTime")
    secs = int(run) * 60 if run and run < 71582788 else None
    return {"level": int(d["EstimatedChargeRemaining"]), "charging": plugged,
            "chargingTime": None, "dischargingTime": None if plugged else secs}


def read_battery():
    system = platform.system()
    try:
        if system == "Darwin":
            return read_mac()
        if system == "Linux":
            return read_linux()
        if system == "Windows":
            return read_windows()
    except Exception:
        return None
    return None


def make_handler(origin, fake):
    class Handler(BaseHTTPRequestHandler):
        def _headers(self, code, body=b""):
            self.send_response(code)
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self._headers(204)

        def do_GET(self):
            data = {"level": fake, "charging": False, "chargingTime": None, "dischargingTime": 9000} if fake is not None else read_battery()
            if data is None:
                self._headers(503, b'{"error":"No battery found"}')
            else:
                self._headers(200, json.dumps(data).encode())

        def log_message(self, *a):
            pass

    return Handler


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="BatteryTab helper")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--origin", default="*", help="only allow this site, e.g. https://you.github.io")
    ap.add_argument("--fake", type=int, help="serve a fixed fake battery level (testing)")
    a = ap.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(a.origin, a.fake))
    print(f"BatteryTab helper running at http://127.0.0.1:{a.port}/battery  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
