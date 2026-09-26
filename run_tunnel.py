"""
Auto-reconnecting Tunnel Watchdog for MuzzleScan AI
Keeps the public HTTPS tunnel alive 24/7 without manual intervention.
"""
import subprocess
import time
import urllib.request
import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PORT = 8000

def get_public_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as res:
            return res.read().decode("utf-8").strip()
    except Exception:
        return "103.170.179.235"

def run_watchdog():
    ip = get_public_ip()
    print("=" * 65)
    print("  MUZZLESCAN AI - AUTO-RECONNECTING LIVE PUBLIC TUNNEL")
    print(f"  Target Local Port: http://127.0.0.1:{PORT}")
    print(f"  Tunnel Password  : {ip}")
    print("=" * 65)

    while True:
        print("\n[*] Starting tunnel connection...")
        try:
            proc = subprocess.Popen(
                ["npx", "localtunnel", "--port", str(PORT)],
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
                    print("\n" + "=" * 65)
                    print(f"  [ONLINE] LIVE PUBLIC URL: {url}")
                    print(f"  [KEY]    PASSWORD (if prompted): {ip}")
                    print("=" * 65 + "\n")
                    # Save current live URL to a text file for easy reading
                    with open("LIVE_URL.txt", "w", encoding="utf-8") as f:
                        f.write(f"URL: {url}\nPASSWORD: {ip}\n")
                elif line_clean:
                    print(line_clean)

            proc.wait()
            print(f"[!] Tunnel disconnected. Auto-reconnecting in 3 seconds...")
        except Exception as e:
            print(f"[!] Watchdog error: {e}. Retrying in 3 seconds...")

        time.sleep(3)

if __name__ == "__main__":
    run_watchdog()
