# -*- coding: utf-8 -*-
"""
Scheduler Daemon pentru Trimiterea Zilnică a Briefurilor TikTok pe Telegram.
Poate rula continuu în fundal și trimite automat în fiecare dimineață la ora stabilită (implicit 10:00).
"""
import sys
import os
import time
from datetime import datetime

# Asigură codificarea UTF-8 pe Windows console
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from automation.run_daily_tiktok import main as run_dispatch, load_state

TARGET_HOUR = int(os.getenv("TIKTOK_SCHEDULE_HOUR", "10"))  # Ora 10:00 dimineața
TARGET_MINUTE = int(os.getenv("TIKTOK_SCHEDULE_MINUTE", "0"))

def run_loop():
    print(f"[*] LexCivic TikTok Telegram Daemon pornit.")
    print(f"[*] Programat zilnic la ora {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} (ora României).")
    print("[*] Apăsați Ctrl+C pentru oprire.\n")

    last_sent_day = None

    # Verifică istoricul din state.json pentru a nu trimite dublu în aceeași zi
    state = load_state()
    history = state.get("history", [])
    if history:
        try:
            last_dt = datetime.fromisoformat(history[-1]["sent_at"])
            last_sent_day = last_dt.date()
        except Exception:
            pass

    while True:
        now = datetime.now()
        current_date = now.date()

        # Condiție: ora curentă coincide sau depășește ora țintă și nu a fost trimis astăzi
        if now.hour == TARGET_HOUR and now.minute == TARGET_MINUTE:
            if last_sent_day != current_date:
                print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Este ora programată! Se trimite brieful TikTok...")
                try:
                    # Rulam procesul de trimitere și avansare
                    sys.argv = ["run_daily_tiktok.py"]
                    run_dispatch()
                    last_sent_day = current_date
                except Exception as e:
                    print(f"[-] Eroare la trimitere: {e}")
                time.sleep(65)  # Așteaptă să treacă minutul
        time.sleep(30)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        print("[*] Trimitere imediată forțată...")
        sys.argv = ["run_daily_tiktok.py"]
        run_dispatch()
    else:
        run_loop()
