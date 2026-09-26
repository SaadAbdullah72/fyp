"""
Auto-reconnecting Tunnel Watchdog with Persistent Subdomain & Keep-Alive Ping
Keeps your public link permanently alive and fixed to a single URL.
"""
import subprocess
import time
import urllib.request
import os
import sys
import threading

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PORT = 8000
SUBDOMAIN = "muzzlescan-fyp"
current_url = f"https://{SUBDOMAIN}.loca.lt"
is_running = True

def get_public_ip():
    try:
        req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.read().decode("utf-8").strip()
    except Exception:
        return "103.170.179.235"

def keep_alive_worker():
    """
    Sends a heartbeat ping every 25 seconds through the tunnel
    to prevent localtunnel.me free servers from dropping idle TCP connections.
    """
    global is_running, current_url
    time.sleep(10)
    while is_running:
        try:
            if current_url:
                req = urllib.request.Request(
                    f"http://127.0.0.1:{PORT}/api/registry",
                    headers={"User-Agent": "Tunnel-Heartbeat/2.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    pass
        except Exception:
            pass
        time.sleep(25)

def run_watchdog():
    global current_url
    ip = get_public_ip()
    print("=" * 65)
    print("  MUZZLESCAN AI - PERMANENT PUBLIC TUNNEL WATCHDOG")
    print(f"  Target Local Port: http://127.0.0.1:{PORT}")
    print(f"  Fixed Subdomain  : {SUBDOMAIN}")
    print(f"  Persistent URL   : https://{SUBDOMAIN}.loca.lt")
    print(f"  Bypass Password  : {ip}")
    print("=" * 65)

    # Start Keep-Alive Heartbeat in background
    heartbeat_thread = threading.Thread(target=keep_alive_worker, daemon=True)
    heartbeat_thread.start()

    while True:
        print("\n[*] Initializing permanent tunnel connection...")
        try:
            proc = subprocess.Popen(
                ["npx", "localtunnel", "--port", str(PORT), "--subdomain", SUBDOMAIN],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                shell=True
            )

            for line in proc.stdout:
                line_clean = line.strip()
                if "your url is:" in line_clean:
                    url = line_clean.split("your url is:")[-1].strip()
                    current_url = url
                    print("\n" + "=" * 65)
                    print(f"  [ONLINE] FIXED PUBLIC URL: {url}")
                    print(f"  [KEY]    PASSWORD (if prompted): {ip}")
                    print("  [STATUS] Heartbeat Active (Zero-Disconnect Mode)")
                    print("=" * 65 + "\n")
                    
                    with open("LIVE_URL.txt", "w", encoding="utf-8") as f:
                        f.write(f"URL: {url}\nPASSWORD: {ip}\nFIXED_SUBDOMAIN: {SUBDOMAIN}\n")
                elif line_clean:
                    print(line_clean)

            proc.wait()
            print(f"[!] Tunnel disconnected. Auto-reconnecting to https://{SUBDOMAIN}.loca.lt in 3 seconds...")
        except Exception as e:
            print(f"[!] Watchdog error: {e}. Retrying in 3 seconds...")

        time.sleep(3)

if __name__ == "__main__":
    run_watchdog()
