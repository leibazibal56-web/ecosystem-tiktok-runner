# -*- coding: utf-8 -*-
"""
Public Cloud Runner Orchestrator for all 30 Ecosystem TikTok Video Generators.
Runs on GitHub Actions (Public Repository -> Unlimited Free Minutes) using GitHub Encrypted Secrets.
"""
import os
import sys
import time
import subprocess
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALL_30_APPS = [
    ("intelligent-studio", "Intelligent Studio", "08:00", 8, 0),
    ("lexsinteza", "LexSinteză", "08:30", 8, 30),
    ("lex-admitere", "Lex Studio", "09:00", 9, 0),
    ("lex-civic", "LexCivic", "09:30", 9, 30),
    ("academic-copilot", "Academic Research Co-pilot", "10:00", 10, 0),
    ("medstudio", "MedStudio", "10:30", 10, 30),
    ("cadet-studio", "CadetStudio", "11:00", 11, 0),
    ("catedra-titularizare-definitivat", "Catedra — Titularizare & Definitivat", "11:30", 11, 30),
    ("poli_prep_app", "PoliPrep UPB", "12:00", 12, 0),
    ("sesiune-studio", "SesiuneStudio", "12:30", 12, 30),
    ("govtalent-romania", "GovTalent România", "13:00", 13, 0),
    ("cariera-privat-ro", "CarieraPrivat România", "13:30", 13, 30),
    ("cariera-privat-absolventi", "CarieraPrivat Absolvenți", "14:00", 14, 0),
    ("vocastudio", "VocaStudio", "14:30", 14, 30),
    ("traiectoria-academica", "Traiectoria Academică", "15:00", 15, 0),
    ("veritas-romania", "Veritas România", "15:30", 15, 30),
    ("lexplicit", "LexPlicit", "16:00", 16, 0),
    ("cetatenie-romana", "Cetățenie Română Didactic", "16:30", 16, 30),
    ("metodika-edu", "Metodika Edu AI", "17:00", 17, 0),
    ("lingvo-romania", "Lingvo România", "17:30", 17, 30),
    ("lsp-romania-app", "LSP România", "18:00", 18, 0),
    ("worksafe-ssm", "WorkSafe SSM & PSI", "18:30", 18, 30),
    ("navigator-romania", "Navigator România", "19:00", 19, 0),
    ("anre-electrician-pro", "ANRE Electrician Pro", "19:30", 19, 30),
    ("finstudio", "FinStudio România", "20:00", 20, 0),
    ("sanitasstudio", "SanitasStudio", "20:30", 20, 30),
    ("safeiscir", "SafeISCIR România", "21:00", 21, 0),
    ("transpstudio", "TranspStudio ARR", "21:30", 21, 30),
    ("techstudio", "TechStudio IT", "22:00", 22, 0),
    ("traducator-autorizat-app", "Traducător Autorizat MJ", "22:30", 22, 30),
]

def get_ro_time() -> datetime:
    return datetime.now(timezone(timedelta(hours=3)))

def run_app(app_id: str, app_name: str) -> bool:
    app_dir = os.path.join(BASE_DIR, "generators", app_id)
    script_path = os.path.join(app_dir, "scripts", "tiktok_daily_generator.py")
    if not os.path.isfile(script_path):
        print(f"[!] Script not found for {app_id}: {script_path}", flush=True)
        return False
    print(f"\n=======================================================", flush=True)
    print(f"🚀 RUNNING TIKTOK GENERATOR: {app_name} ({app_id})", flush=True)
    print(f"=======================================================", flush=True)
    res = subprocess.run([sys.executable, script_path], cwd=app_dir)
    ok = (res.returncode == 0)
    print(f"[{'OK' if ok else 'FAIL'}] {app_name} finished with code {res.returncode}", flush=True)
    return ok

def main():
    target = (sys.argv[1] if len(sys.argv) > 1 else os.getenv("TARGET_APP") or "due").strip()
    ro_now = get_ro_time()
    print(f"[*] Ecosystem TikTok Cloud Runner | RO Time: {ro_now.strftime('%Y-%m-%d %H:%M:%S')} | Target: {target}", flush=True)

    app_map = {a[0]: a for a in ALL_30_APPS}

    if target == "all":
        selected = ALL_30_APPS
    elif target == "due":
        now_mins = ro_now.hour * 60 + ro_now.minute
        # Select apps scheduled within the last 35 minutes
        selected = []
        for a in ALL_30_APPS:
            sched_mins = a[3] * 60 + a[4]
            if 0 <= (now_mins - sched_mins) < 30:
                selected.append(a)
        if not selected:
            # Fallback to deterministic slot based on hour so scheduled cron always produces the slot's app
            idx = ((ro_now.hour * 2) + (1 if ro_now.minute >= 30 else 0)) % len(ALL_30_APPS)
            selected = [ALL_30_APPS[idx]]
    elif "," in target:
        ids = [x.strip() for x in target.split(",") if x.strip()]
        selected = [app_map[i] for i in ids if i in app_map]
    elif target in app_map:
        selected = [app_map[target]]
    else:
        print(f"[!] Unknown target '{target}'. Valid app IDs: {list(app_map.keys())}", flush=True)
        sys.exit(1)

    failures = 0
    for app_id, app_name, _, _, _ in selected:
        if not run_app(app_id, app_name):
            failures += 1
        if len(selected) > 1:
            time.sleep(2)

    if failures > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
