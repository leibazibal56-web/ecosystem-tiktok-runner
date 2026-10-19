# -*- coding: utf-8 -*-
"""
CarieraPro România - TikTok, Reels & Shorts Daily Automation Pipeline
======================================================================
Modul: scripts/tiktok_daily_generator.py

Funcționalități:
1. Generare videoclipuri verticale 9:16 (1080x1920) cu subtitrări animate sincronizate (karaoke highlight).
2. Voce umană, caldă, feminină și autoritară profesional (Gemini TTS Aoede / Edge-TTS ro-RO-AlinaNeural).
3. 4 Formate narative rotative de mare impact pentru candidații la joburi în mediul privat și corporativ.
4. Generare scenarii noi zilnice prin Gemini 2.5 Flash, cu 4 fallback-uri de calitate superioară gata pregătite.
5. Livrare automată directă pe canalul / chat-ul de Telegram al administratorului cu casetă 'click-to-copy' pentru postare rapidă pe TikTok.
"""

import os
import sys
import json
import time
import random
import asyncio
import subprocess
import requests
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

load_dotenv(os.path.join(ROOT_DIR, ".env"))

# ── Credențiale & Configurare Ecosistem ──────────────────────────────────
GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "8867321650").strip()
APP_URL = os.getenv("APP_URL") or "https://cariera-pro-romania.vercel.app/"

OUTPUT_DIR = os.path.abspath(os.path.join(ROOT_DIR, "video-generator"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "carierapro_audio.wav")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "carierapro_tiktok.mp4")

# ── 4 Scenarii Fallback de Calitate Superioară (Piața Muncii & Corporații) ─
FALLBACK_TOPICS = [
    {
        "topic_title": "3 GREȘELI FATALE LA INTERVIUL PENTRU MEDIUL PRIVAT",
        "alert_badge": "INTERVIU CORPORATIV",
        "script_speech": "Mergi la un interviu pentru o multinațională sau o companie privată? Iată trei greșeli fatale care te pot descalifica instant! Unu: Capcana modestiei. Dacă spui 'am făcut noi' sau 'ne-am propus', recrutorul nu știe ce ai făcut TU. Folosește persoana întâi singular: 'am decis', 'am calculat', 'am optimizat'! Doi: Vorbești prea mult despre context și omiți acțiunea. La metoda STAR, șaizeci la sută din răspuns trebuie să fie despre pașii tăi concreți. Trei: Nu știi că recrutorul nu are voie legal să te întrebe salariul anterior conform Directivei Europene de Transparență! Testează-ți răspunsurile STAR gratuit pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "3 GREȘELI FATALE LA INTERVIU", "color": "#DC2626"},
            {"time_max": 14.0, "text": "1 • CAPCANA MODESTIEI: NOI VS EU", "color": "#2563EB"},
            {"time_max": 21.5, "text": "2 • REGULA 60% ACȚIUNE ÎN STAR", "color": "#D97706"},
            {"time_max": 27.5, "text": "3 • SALARIUL VECHI ESTE SECRET", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • SIMULATOR STAR GRATUIT", "color": "#10B981"}
        ],
        "tiktok_caption": "Nu pica interviul din cauza capcanei modestiei sau a lipsei de structură! Cele 3 secrete ale interviului STAR în corporații explicate. Antrenează-te gratuit pe https://cariera-pro-romania.vercel.app/ ! 💼🚀 #cariera #interviu #angajare #corporatie #starinterview #salariu #carierastart #jobromania"
    },
    {
        "topic_title": "DE CE ÎȚI RESPINGE ATS-UL CV-UL ÎN 10 SECUNDE?",
        "alert_badge": "SCANNER ATS 2026",
        "script_speech": "Trimiți zeci de CV-uri și nu te sună nimeni pentru interviu? Problema nu ești tu, ci sistemul automat ATS! Peste optzeci și cinci la sută din marile companii filtrează CV-urile prin roboți înainte să ajungă la un om. Iată de ce ești respins: Barele procentuale de abilități precum 'Engleză 80%' corup parsarea optică a robotului! La fel și CV-urile aranjate pe două coloane sau tabelele complexe. Soluția este un PDF nativ pe o singură pagină, redactat după formula X-Y-Z: Verb de acțiune, plus context, plus rezultat măsurabil. Scanează-ți CV-ul acum pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "DE CE ÎȚI RESPINGE ROBOTUL CV-UL?", "color": "#EF4444"},
            {"time_max": 14.0, "text": "CAPCANA 1: BARELE DE PROCENTE 80%", "color": "#F59E0B"},
            {"time_max": 21.5, "text": "CAPCANA 2: TABELE PE 2 COLOANE", "color": "#DC2626"},
            {"time_max": 27.5, "text": "FORMULA SALVATOARE: X - Y - Z", "color": "#2563EB"},
            {"time_max": 99.0, "text": "SOLUȚIE • SCANNER CV ATS GRATUIT", "color": "#10B981"}
        ],
        "tiktok_caption": "Știai că robotul ATS îți respinge CV-ul din cauza barelor de procente sau a tabelelor? Cum construiești un CV care trece orice filtru corporativ. Verifică scorul CV-ului tău pe https://cariera-pro-romania.vercel.app/ ! 📄🤖 #cv #ats #resurseumane #recrutare #locuridemunca #carierastart #angajari"
    },
    {
        "topic_title": "ATENȚIE: CELE 90 DE ZILE DE PROBĂ DIN CODUL MUNCII!",
        "alert_badge": "ARTICOLUL 31 CODUL MUNCII",
        "script_speech": "Ai semnat primul contract de muncă? Atenție mare la Articolul 31 din Codul Muncii! Pentru funcțiile de execuție, perioada de probă este de maximum nouăzeci de zile calendaristice. În acest interval, compania te poate concedia într-o singură secundă, printr-o simplă notificare scrisă, fără preaviz și fără nicio motivare! Cum te protejezi? Aplică planul strategic treizeci, șaizeci, nouăzeci de zile și folosește regula celor două soluții: nu duce niciodată o problemă managerului fără să ai pregătite două variante de rezolvare. Descarcă planul complet de pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "PERIOADA DE PROBĂ: REGULI DURE", "color": "#DC2626"},
            {"time_max": 14.0, "text": "MAXIM 90 ZILE CALENDARISTICE", "color": "#F59E0B"},
            {"time_max": 21.5, "text": "FĂRĂ PREAVIZ ȘI FĂRĂ MOTIVARE", "color": "#DC2626"},
            {"time_max": 27.5, "text": "REGULA CELOR 2 SOLUȚII RAPIDE", "color": "#2563EB"},
            {"time_max": 99.0, "text": "SOLUȚIE • PLANUL 30-60-90 ZILE", "color": "#10B981"}
        ],
        "tiktok_caption": "Ce drepturi ai cu adevărat în cele 90 de zile de probă? Ce prevede Articolul 31 din Codul Muncii și cum eviți concedierea instantanee fără motivare. Descarcă ghidul pe https://cariera-pro-romania.vercel.app/ ! ⚖️🏢 #codulmuncii #perioadadeproba #angajat #dreptulmuncii #corporatie #carierastart"
    },
    {
        "topic_title": "CÂT SE CÂȘTIGĂ NET ȘI CUM NEGOCIEZI LEGAL ÎN 2026",
        "alert_badge": "TRANSPARENȚĂ SALARIALĂ",
        "script_speech": "Cât se câștigă cu adevărat la debut în mediul privat? Conform datelor agregate, salariul mediu net de intrare este de patru mii două sute de lei în București și trei mii nouă sute de lei în Cluj, Timișoara și Iași. De la șapte iunie douăzeci douăzeci și șase, Directiva Europeană obligă companiile să publice grila de salariu și le interzice să-ți ceară fluturașul de la jobul anterior! Iar dacă ai fost intern, amintește-i recrutorului de Legea 176 pe 2018: compania primește o subvenție de peste patru mii cinci sute de lei dacă te angajează pe doi ani! Calculează-ți pachetul complet pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "SALARII ENTRY-LEVEL ÎN ROMÂNIA", "color": "#3B82F6"},
            {"time_max": 13.5, "text": "BUCUREȘTI 4200 • CLUJ/TM 3900", "color": "#2563EB"},
            {"time_max": 20.5, "text": "DIRECTIVA UE: TRANSPARENȚĂ 2026", "color": "#10B981"},
            {"time_max": 27.0, "text": "SUBVENȚIE 4586 LEI PRIN LEGE", "color": "#F59E0B"},
            {"time_max": 99.0, "text": "SOLUȚIE • CALCULATOR SALARIAL PRO", "color": "#10B981"}
        ],
        "tiktok_caption": "Cât este salariul net de debut în București, Cluj și Timișoara? Cum folosești Directiva de Transparență și Legea Internshipului pentru a negocia cu 15% mai mult. Calculează pe https://cariera-pro-romania.vercel.app/ ! 💰📊 #salariu #negociere #bani #transparentasalariala #drepturilamunca #carierastart"
    }
]

# ── Font Loader (Windows & Linux Support) ─────────────────────────────────
def get_font(size, bold=True):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf",
        "arialbd.ttf",
        "Arial Bold.ttf"
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

# ── 1. Generare Scenariu prin Gemini 2.5 Flash ────────────────────────────
ROTATING_FORMATS = [
    {
        "id": "top3_interview_traps",
        "name": "TOP 3 CAPCANE / GREȘELI LA INTERVIUL PENTRU MEDIUL PRIVAT",
        "instruction": (
            "FORMATUL 1: TOP 3 CAPCANE LA INTERVIUL CORPORATIV. "
            "Structură: Începe cu un Hook alert (primele 4 secunde) despre pericolele care descalifică un candidat la interviu. "
            "Urmează 3 puncte numerotate Unu / Doi / Trei (solide, concise, legate de metoda STAR, capcana modestiei 'noi vs eu', drepturile la negociere) "
            "și un îndemn final de testare pe " + APP_URL + "."
        ),
        "section_structure": "Secțiunea 1 (problemă #DC2626), Punctul 1 (#2563EB), Punctul 2 (#D97706), Punctul 3 (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "ats_cv_myth",
        "name": "MIT VS. REALITATE: DE CE ÎȚI RESPINGE ATS-UL CV-UL",
        "instruction": (
            "FORMATUL 2: MIT VS. REALITATE LA FILTRAREA CV-ULUI PRIN ATS. "
            "Structură: Începe cu 'Trimiți zeci de CV-uri și nu primești niciun răspuns? Iată de ce!'. "
            "Explică de ce barele de procente, tabelele pe 2 coloane sau CV-urile încărcate grafic blochează parsarea automată, "
            "oferă formula corectă X-Y-Z (Verb + Context + Rezultat) și îndemnul de scanare pe " + APP_URL + "."
        ),
        "section_structure": "Secțiunea 1 (titlu mit #EF4444), De ce e fals (#F59E0B), Realitatea corectă (#2563EB), Formula X-Y-Z (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "probation_law",
        "name": "PERIOADA DE PROBĂ - CE PREVEDE ART. 31 CODUL MUNCII",
        "instruction": (
            "FORMATUL 3: CELE 90 DE ZILE DE PROBĂ DIN CODUL MUNCII. "
            "Structură: Începe cu 'Ai semnat primul contract? Atenție mare la perioada de probă!'. "
            "Explică regimul celor 90 de zile pentru execuție (încetare fără preaviz și fără motivare) și cum te salvează planul 30-60-90 zile și regula celor două soluții, "
            "urmat de îndemnul de descărcare pe " + APP_URL + "."
        ),
        "section_structure": "Secțiunea 1 (dilemă #DC2626), Greșeala comună (#F59E0B), Regula Art. 31 (#2563EB), Regula celor 2 soluții (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "salary_transparency",
        "name": "TRANSPARENȚĂ SALARIALĂ & SUBVENȚII LEGALE LA ANGAJARE",
        "instruction": (
            "FORMATUL 4: CÂT SE CÂȘTIGĂ NET ȘI CUM NEGOCIEZI LEGAL ÎN 2026. "
            "Structură: Începe cu 'Cât este salariul net de debut în marile orașe din România?'. "
            "Prezintă mediile salariale (București 4200 lei, Cluj/Timișoara 3900 lei), Directiva UE de transparență (fără întrebări despre salariul vechi) și subvenția de 4586 lei din Legea 176/2018, "
            "urmat de îndemnul de calculare pe " + APP_URL + "."
        ),
        "section_structure": "Secțiunea 1 (titlu salarii #3B82F6), Repere regionale (#2563EB), Directiva UE (#10B981), Subvenția legală (#F59E0B), CTA final (#10B981)."
    }
]

def generate_scenario_with_gemini():
    import datetime
    day_idx = datetime.datetime.now().timetuple().tm_yday % len(ROTATING_FORMATS)
    chosen_format = ROTATING_FORMATS[day_idx]
    print(f"[1/4] Solicitare scenariu nou prin Gemini 2.5 Flash (Format: {chosen_format['name']})...")

    if not GEMINI_API_KEY:
        return FALLBACK_TOPICS[day_idx % len(FALLBACK_TOPICS)]

    prompt = (
        f"Ești scenaristul oficial pentru conținutul video scurt (TikTok / Reels / YouTube Shorts) al platformei CarieraStart ({APP_URL}) - platforma strategică dedicată absolvenților și candidaților pentru ocuparea posturilor în mediul privat și corporativ.\n\n"
        f"NORME OBLIGATORII PRIVIND LIMBA ROMÂNĂ (DOOM3 / ACADEMIA ROMÂNĂ):\n"
        f"- Folosește EXCLUSIV LIMBA ROMÂNĂ OFICIALĂ LITERARĂ, conform normelor ortografice și morfologice oficiale (DOOM3).\n"
        f"- Este STRICT INTERZISĂ orice greșeală gramaticală sau ortografică (folosește diacritice corecte: ă, â, î, ș, ț).\n"
        f"- Tonul este energic, profesionist, asertiv, captivant și adaptat candidaților care intră pe piața muncii private.\n\n"
        f"Astăzi vei crea un scenariu conform acestui stil narativ obligatoriu:\n"
        f"{chosen_format['instruction']}\n\n"
        f"Ghidaj secțiuni grafice: {chosen_format['section_structure']}\n"
        f"Domenii recomandate: Formula STAR la interviu (alocare 60% pe acțiune la persoana I), filtrarea ATS (eliminare grafice, formulare X-Y-Z), Directiva UE 2023/970 (transparență salarială, confidențialitatea salariului anterior), Art. 31 Codul Muncii (perioada de probă de 90 zile), Legea 176/2018 (subvenție 4.586 lei pt angajator).\n\n"
        f"Scenariul trebuie să aibă 25-30 de secunde (aproximativ 65-75 de cuvinte).\n"
        "RĂSPUNDE EXCLUSIV ÎN FORMAT JSON VALID conform acestei scheme fără comentarii sau markdown:\n"
        "{\n"
        '  "topic_title": "TITLU CU MAJUSCULE (max 6 cuvinte)",\n'
        '  "alert_badge": "CATEGORIE SUBIECT (max 3 cuvinte)",\n'
        '  "script_speech": "Textul rostit în limba română (65-75 cuvinte), cursiv, ritmat, respectând formatul de mai sus.",\n'
        '  "sections": [\n'
        '    {"time_max": 6.5, "text": "TITLU INTRO / FORMAT", "color": "#DC2626"},\n'
        '    {"time_max": 14.0, "text": "PUNCTUL 1", "color": "#2563EB"},\n'
        '    {"time_max": 21.5, "text": "PUNCTUL 2", "color": "#F59E0B"},\n'
        '    {"time_max": 27.5, "text": "PUNCTUL 3 / CONCLUZIE", "color": "#DC2626"},\n'
        '    {"time_max": 99.0, "text": "SOLUȚIE • VERIFICĂ ACUM", "color": "#10B981"}\n'
        '  ],\n'
        '  "tiktok_caption": "Descriere captivantă pentru TikTok incluzând linkul ' + APP_URL + ' și 4-6 hashtag-uri relevante: #cariera #interviu #angajare #cv #ats #salariu #carierastart"\n'
        "}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.75, "topP": 0.95}
    }
    try:
        res = requests.post(url, json=payload, timeout=45)
        if res.status_code == 200:
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1]
            if raw_text.endswith("```"):
                raw_text = raw_text.rsplit("\n", 1)[0]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()
            parsed = json.loads(raw_text)
            print(f"✅ Scenariu generat cu succes ({chosen_format['name']}): {parsed.get('topic_title')}")
            return parsed
        else:
            print(f"Atenție: Răspuns Gemini {res.status_code}. Se trece pe fallback.")
            return FALLBACK_TOPICS[day_idx % len(FALLBACK_TOPICS)]
    except Exception as e:
        print(f"Atenție apel Gemini: {e}. Se trece pe fallback.")
        return FALLBACK_TOPICS[day_idx % len(FALLBACK_TOPICS)]

# ── 2. Generare Voce Umană, Caldă & Atractivă ─────────────────────────────
def compute_word_timestamps(script_text, total_duration):
    words = script_text.split()
    weights = []
    for w in words:
        clean = w.rstrip(".,?!:;")
        base = max(1, len(clean))
        if any(w.endswith(p) for p in [".", "?", "!"]):
            pause = 3.5
        elif any(w.endswith(p) for p in [",", ":", ";"]):
            pause = 2.0
        else:
            pause = 0.0
        weights.append(base + pause)
        
    total_w = sum(weights)
    scale = (total_duration - 0.4) / total_w
    
    cur_t = 0.25
    timed = []
    for i, w in enumerate(words):
        dur = weights[i] * scale
        clean_len = max(1, len(w.rstrip(".,?!:;")))
        speak_dur = max(0.18, (clean_len / weights[i]) * dur)
        timed.append({
            "text": w,
            "start": cur_t,
            "end": cur_t + speak_dur
        })
        cur_t += dur
    return timed

async def generate_audio_and_timestamps(script_text):
    print("[2/4] Generare voce umană, feminină, caldă & atractivă (Gemini Aoede / Edge-TTS)...")
    import base64
    import wave

    tts_models = [
        "gemini-2.5-flash-preview-tts",
        "gemini-3.1-flash-tts-preview",
        "gemini-2.5-pro-preview-tts"
    ]

    prompt = (
        f"""Citește cu o voce feminină deosebit de profesionistă, caldă, foarte sigură, energică și perfect naturală în limba română următorul ghid de carieră dedicat candidaților din mediul corporativ:

{script_text}"""
    )

    if GEMINI_API_KEY:
        for model in tts_models:
            for attempt in range(2):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "responseModalities": ["AUDIO"],
                            "speechConfig": {
                                "voiceConfig": {
                                    "prebuiltVoiceConfig": {"voiceName": "Aoede"}
                                }
                            }
                        }
                    }
                    res = requests.post(url, json=payload, timeout=60)
                    if res.status_code == 200:
                        data = res.json()
                        cand = data.get("candidates", [])[0]
                        parts = cand.get("content", {}).get("parts", [])
                        for part in parts:
                            if "inlineData" in part and part["inlineData"].get("mimeType", "").startswith("audio/"):
                                audio_bytes = base64.b64decode(part["inlineData"]["data"])
                                with open(AUDIO_PATH, "wb") as f:
                                    f.write(audio_bytes)
                                
                                with wave.open(AUDIO_PATH, "rb") as wf:
                                    frames = wf.getnframes()
                                    rate = wf.getframerate()
                                    duration = frames / float(rate)
                                
                                timed_words = compute_word_timestamps(script_text, duration)
                                print(f"✅ Voce generată prin Gemini TTS ({model} - Aoede): {duration:.2f}s ({len(timed_words)} cuvinte)")
                                return duration, timed_words
                except Exception as e:
                    time.sleep(1)

    print("ℹ️ Fallback activat: Generare voce prin Edge-TTS (ro-RO-AlinaNeural)...")
    try:
        import edge_tts
        VOICE = "ro-RO-AlinaNeural"
        communicate = edge_tts.Communicate(script_text, VOICE, rate="+3%", pitch="+0Hz")
        
        timed_words = []
        with open(AUDIO_PATH, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    timed_words.append({
                        "text": chunk["text"],
                        "start": chunk["offset"] / 10_000_000,
                        "end": (chunk["offset"] + chunk["duration"]) / 10_000_000
                    })
        
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [ffmpeg_bin, "-i", AUDIO_PATH]
        proc = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, errors="ignore")
        import re
        dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr)
        if dur_match:
            duration = int(dur_match.group(1))*3600 + int(dur_match.group(2))*60 + float(dur_match.group(3))
        else:
            duration = (timed_words[-1]["end"] + 0.5) if timed_words else 26.0

        if not timed_words:
            timed_words = compute_word_timestamps(script_text, duration)

        print(f"✅ Voce generată prin Edge-TTS ({VOICE}): {duration:.2f}s")
        return duration, timed_words
    except Exception as e:
        print(f"Eroare Edge-TTS: {e}. Se generează audio de rezervă.")
        duration = 26.0
        timed_words = compute_word_timestamps(script_text, duration)
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [ffmpeg_bin, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(duration), AUDIO_PATH]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return duration, timed_words

# ── 3. Render Cadre & Compoziție Video 9:16 (1080x1920) ───────────────────
def render_video_frames(scenario, duration, timed_words):
    print("[3/4] Generare videoclip vertical 9:16 (1080x1920) cu subtitrări dinamice...")
    
    WIDTH = 1080
    HEIGHT = 1920
    FPS = 30
    TOTAL_FRAMES = int(duration * FPS)

    font_badge = get_font(32, bold=True)
    font_title = get_font(52, bold=True)
    font_section = get_font(40, bold=True)
    font_sub_normal = get_font(46, bold=False)
    font_sub_highlight = get_font(48, bold=True)
    font_footer = get_font(36, bold=True)
    font_url = get_font(42, bold=True)

    base_bg = Image.new("RGB", (WIDTH, HEIGHT), color="#0F172A")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(15 * (1 - ratio) + 30 * ratio)
        g = int(23 * (1 - ratio) + 41 * ratio)
        b = int(42 * (1 - ratio) + 89 * ratio)
        draw_bg.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Header Card
    draw_bg.rounded_rectangle([60, 80, WIDTH - 60, 420], radius=28, fill="#1E293B", outline="#3B82F6", width=3)
    
    badge_text = f"● {scenario.get('alert_badge', 'CARIERASTART 2026')}"
    top_pill_w = max(420, int(draw_bg.textlength(badge_text, font=font_badge)) + 48)
    draw_bg.rounded_rectangle([100, 115, min(WIDTH - 100, 100 + top_pill_w), 175], radius=16, fill="#2563EB")
    draw_bg.text((124, 126), badge_text, font=font_badge, fill="#FFFFFF")

    # Title with wrapping
    title_text = scenario.get("topic_title", "GHID STRATEGIC PENTRU MEDIUL PRIVAT")
    words_title = title_text.split()
    lines_title = []
    cur_line = []
    for w in words_title:
        cur_line.append(w)
        if len(" ".join(cur_line)) > 24:
            lines_title.append(" ".join(cur_line[:-1]))
            cur_line = [w]
    if cur_line:
        lines_title.append(" ".join(cur_line))
    
    y_title = 205
    for l in lines_title[:3]:
        draw_bg.text((100, y_title), l, font=font_title, fill="#FFFFFF")
        y_title += 65

    # Footer Card
    draw_bg.rounded_rectangle([60, HEIGHT - 340, WIDTH - 60, HEIGHT - 80], radius=28, fill="#0F172A", outline="#10B981", width=3)
    cta_label = "ACCESEAZĂ PLATFORMA"
    cta_pill_w = int(draw_bg.textlength(cta_label, font=font_badge)) + 48
    draw_bg.rounded_rectangle([100, HEIGHT - 315, 100 + cta_pill_w, HEIGHT - 260], radius=14, fill="#10B981")
    draw_bg.text((124, HEIGHT - 305), cta_label, font=font_badge, fill="#0F172A")
    draw_bg.text((100, HEIGHT - 235), "cariera-pro-romania.vercel.app", font=font_url, fill="#38BDF8")
    draw_bg.text((100, HEIGHT - 165), "CarieraStart • ATS Scanner • Interviu STAR", font=font_footer, fill="#94A3B8")

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", AUDIO_PATH,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        VIDEO_PATH
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    sections = scenario.get("sections", [])
    
    for f in range(TOTAL_FRAMES):
        cur_t = f / FPS
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)

        # Dynamic Section Banner (Top Section Box)
        active_sec = None
        for s in sections:
            if cur_t <= s.get("time_max", 99.0):
                active_sec = s
                break
        if not active_sec and sections:
            active_sec = sections[-1]

        sec_text = active_sec.get("text", "GHID CARIERĂ") if active_sec else "GHID CARIERĂ"
        sec_color = active_sec.get("color", "#2563EB") if active_sec else "#2563EB"

        draw.rounded_rectangle([60, 460, WIDTH - 60, 570], radius=22, fill="#1E293B", outline=sec_color, width=3)
        draw.rounded_rectangle([80, 480, 110, 550], radius=8, fill=sec_color)
        draw.text((130, 495), sec_text[:38], font=font_section, fill="#FFFFFF")

        # Dynamic Subtitles Box with Karaoke Highlight (Middle)
        draw.rounded_rectangle([60, 620, WIDTH - 60, HEIGHT - 390], radius=28, fill="#0F172A", outline="#334155", width=2)
        
        # Word selection window (around current time)
        visible_words = []
        target_idx = -1
        for idx, tw in enumerate(timed_words):
            if tw["start"] <= cur_t <= tw["end"] + 0.15:
                target_idx = idx
                break
        if target_idx == -1:
            for idx, tw in enumerate(timed_words):
                if tw["start"] > cur_t:
                    target_idx = max(0, idx - 1)
                    break
        if target_idx == -1 and timed_words:
            target_idx = len(timed_words) - 1

        start_slice = max(0, target_idx - 7)
        end_slice = min(len(timed_words), target_idx + 8)
        chunk = timed_words[start_slice:end_slice]

        sub_lines = []
        cur_sub_line = []
        for w in chunk:
            cur_sub_line.append(w)
            if len(" ".join([x["text"] for x in cur_sub_line])) > 20:
                sub_lines.append(cur_sub_line)
                cur_sub_line = []
        if cur_sub_line:
            sub_lines.append(cur_sub_line)

        y_sub = 750
        for l in sub_lines[:7]:
            line_str = " ".join([x["text"] for x in l])
            total_w = draw.textlength(line_str, font=font_sub_normal)
            x_start = (WIDTH - total_w) / 2
            
            x_cur = x_start
            for w in l:
                is_active = (w["start"] <= cur_t <= w["end"] + 0.1)
                w_str = w["text"] + " "
                if is_active:
                    draw.rounded_rectangle([x_cur - 6, y_sub - 4, x_cur + draw.textlength(w_str, font=font_sub_highlight) + 4, y_sub + 56], radius=10, fill="#FEF08A")
                    draw.text((x_cur, y_sub), w_str, font=font_sub_highlight, fill="#0F172A")
                else:
                    draw.text((x_cur, y_sub), w_str, font=font_sub_normal, fill="#E2E8F0")
                x_cur += draw.textlength(w_str, font=font_sub_normal)
            y_sub += 75

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"✅ Videoclip generat cu succes: {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH)/1024/1024:.2f} MB)")

# ── 4. Telegram Dispatch ──────────────────────────────────────────────────
def dispatch_to_telegram(scenario):
    print("[4/4] Livrare automată pe canalul Telegram al administratorului...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Atenție: Credențialele Telegram nu sunt configurate.")
        return

    caption = scenario.get("tiktok_caption", f"Pregătește-te pentru cariera ta în mediul privat pe {APP_URL} !")
    
    # Text ajutător de copiat cu 1 click
    msg_intro = (
        f"🚀 <b>CarieraStart — Videoclip TikTok Nou Generat!</b>\n\n"
        f"📌 <b>Titlu:</b> {scenario.get('topic_title')}\n"
        f"🎯 <b>Format:</b> {scenario.get('alert_badge')}\n\n"
        f"📋 <b>Descriere TikTok (Click to Copy):</b>\n"
        f"<code>{caption}</code>\n\n"
        f"🔗 <b>Link Aplicație:</b> {APP_URL}"
    )

    url_msg = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload_msg = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg_intro,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url_msg, json=payload_msg, timeout=20)
    except Exception as e:
        print(f"Eroare trimitere mesaj Telegram: {e}")

    url_vid = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    try:
        with open(VIDEO_PATH, "rb") as vf:
            files = {"video": vf}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": f"🎬 {scenario.get('topic_title')}\n\n{caption[:900]}",
                "supports_streaming": True
            }
            res = requests.post(url_vid, data=data, files=files, timeout=120)
            if res.status_code == 200:
                print("✅ Videoclipul MP4 și descrierea au fost livrate pe Telegram!")
            else:
                print(f"Eroare livrare video Telegram: {res.text}")
    except Exception as e:
        print(f"Excepție trimitere video Telegram: {e}")

    # Salvare manifest local
    pack = {
        "timestamp": int(time.time()),
        "title": scenario.get("topic_title"),
        "badge": scenario.get("alert_badge"),
        "script": scenario.get("script_speech"),
        "caption": caption,
        "video_path": VIDEO_PATH,
        "app_url": APP_URL
    }
    with open(os.path.join(ROOT_DIR, "scripts", "latest_tiktok_pack.json"), "w", encoding="utf-8") as pf:
        json.dump(pack, pf, ensure_ascii=False, indent=2)

    with open(os.path.join(ROOT_DIR, "scripts", "latest_tiktok_pack.txt"), "w", encoding="utf-8") as tf:
        tf.write(f"TITLU: {scenario.get('topic_title')}\n\n")
        tf.write(f"DESCRIERE TIKTOK:\n{caption}\n\n")
        tf.write(f"SCRIPT ROSTIT:\n{scenario.get('script_speech')}\n")

# ── Main Entrypoint ───────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("   CARIERAPRO ROMÂNIA — TIKTOK & REELS DAILY AUTOMATION PIPELINE")
    print("=" * 70)
    
    scenario = generate_scenario_with_gemini()
    duration, timed_words = asyncio.run(generate_audio_and_timestamps(scenario["script_speech"]))
    render_video_frames(scenario, duration, timed_words)
    dispatch_to_telegram(scenario)
    
    print("\n🎉 Pipeline finalizat cu succes! Videoclipul este gata pentru postare.")
    print("=" * 70)

if __name__ == "__main__":
    main()
