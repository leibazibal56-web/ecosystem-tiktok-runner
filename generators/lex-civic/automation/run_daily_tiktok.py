# -*- coding: utf-8 -*-
import sys
import os
import json
import argparse
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

# Asigură includerea directorului rădăcină în sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from automation.tiktok_content_vault import TIKTOK_SCRIPTS, get_script_by_index, get_total_scripts
from automation.telegram_sender import TelegramTikTokDispatcher
from automation.video_generator import TikTokVideoGenerator, VIDEOS_DIR

STATE_FILE = os.path.join(SCRIPT_DIR, "state.json")

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"current_index": 0, "history": []}

def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Warning] Nu s-a putut salva starea: {e}", flush=True)

def main():
    parser = argparse.ArgumentParser(description="LexCivic TikTok Automation to Telegram Dispatcher (Video + Brief)")
    parser.add_argument("--index", type=int, help="Trimite un script specific după index (0-indexed)")
    parser.add_argument("--no-advance", action="store_true", help="Nu avansa indexul după trimitere")
    parser.add_argument("--list", action="store_true", help="Listează toate scenariile disponibile")
    parser.add_argument("--skip-video", action="store_true", help="Trimite doar brieful text fără a genera video")
    parser.add_argument("--force-video", action="store_true", help="Re-generează fișierul video chiar dacă există deja")
    args = parser.parse_args()

    total = get_total_scripts()

    if args.list:
        print(f"\n--- Baza de Scripturi TikTok LexCivic ({total} disponibile) ---")
        for i, s in enumerate(TIKTOK_SCRIPTS):
            print(f"[{i}] {s['title']} ({s['domain']})")
        return

    state = load_state()
    current_idx = state.get("current_index", 0)

    if args.index is not None:
        target_idx = args.index
    else:
        target_idx = current_idx

    script = get_script_by_index(target_idx)
    dispatcher = TelegramTikTokDispatcher()

    print(f"\n=======================================================", flush=True)
    print(f"[*] PROCESARE TIKTOK ZIUA #{target_idx + 1}/{total}", flush=True)
    print(f"[*] Titlu: '{script['title']}' ({script['domain']})", flush=True)
    print(f"=======================================================\n", flush=True)

    video_path = None
    if not args.skip_video:
        expected_video = os.path.join(VIDEOS_DIR, f"{script['id']}.mp4")
        if os.path.exists(expected_video) and not args.force_video:
            print(f"[+] Videoclipul există deja în cache: {expected_video}", flush=True)
            video_path = expected_video
        else:
            print("[*] Generare videoclip 1080x1920 MP4 cu voce română neurală...", flush=True)
            try:
                gen = TikTokVideoGenerator()
                video_path = gen.generate_video_for_script(script, output_path=expected_video)
            except Exception as e:
                print(f"[!] Avertisment: Eroare la generarea video: {e}. Se va trimite brieful text.", flush=True)

    print(f"[*] Se expediază pachetul complet pe Telegram către chat {dispatcher.chat_id}...", flush=True)
    success = dispatcher.dispatch_full_package(script, day_number=target_idx + 1, video_path=video_path)

    if success:
        if not args.no_advance and args.index is None:
            state["current_index"] = (target_idx + 1) % total
            state["history"].append({
                "script_id": script["id"],
                "sent_at": datetime.now().isoformat(),
                "day_number": target_idx + 1,
                "video_generated": bool(video_path and os.path.exists(video_path))
            })
            save_state(state)
        print("\n[+] Pachetul TikTok (Video + Descriere 1-Click + Brief) trimis cu succes pe Telegram!\n", flush=True)
    else:
        print("\n[-] Trimiterea a eșuat. Verificați conexiunea și credențialele Telegram.\n", flush=True)

if __name__ == "__main__":
    main()
