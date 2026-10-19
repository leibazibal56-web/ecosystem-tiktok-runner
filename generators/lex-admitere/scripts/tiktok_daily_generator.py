# -*- coding: utf-8 -*-
"""
Lex Studio TikTok Daily Generator
- Generates 9:16 vertical videos with Gemini 2.5 Flash TTS warm female voice (Aoede) & dynamic subtitles.
- Uses Gemini 2.5 Flash to synthesize fresh legal admission exam traps (Barou, INM, Drept, Notariat).
- Dispatches final MP4 video and copy-paste caption directly to the admin Telegram bot.
- Runs locally on Windows and automatically in GitHub Actions (Ubuntu).
"""
import os
import sys
import json
import random
import asyncio
import subprocess
import requests
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Credentials & Config ──────────────────────────────────────────
GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "8867321650").strip()

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "video-generator"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "daily_audio.wav")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "lex_studio_tiktok.mp4")

# ── Fallback Topics (Barou & INM Law Traps) ────────────────────────
FALLBACK_TOPICS = [
    {
        "topic_title": "3 CAPCANE CLASICE LA GRILELE DE BAROU",
        "alert_badge": "GRILE BAROU & INM",
        "script_speech": "Te pregătești pentru examenul de admitere la Barou sau INM? Iată trei capcane de formulare care păcălesc mii de candidați! Unu: Nuanța dintre nulitatea absolută și cea relativă în materia prescripției. Doi: Neatenția la adverbele de tip exclusiv, întotdeauna sau numai. Trei: Confundarea tentativei pedepsibile cu actele preparatorii. Antrenează-te pe simulatorul de o sută de grile pe lexstudio-ro.vercel.app/studio!",
        "sections": [
            {
                "time_max": 6.5,
                "text": "CAPCANE GRILE ADMITERE",
                "color": "#DC2626"
            },
            {
                "time_max": 14.5,
                "text": "1 • NULITATE & PRESCRIPȚIE",
                "color": "#F59E0B"
            },
            {
                "time_max": 22.5,
                "text": "2 • ADVERBE CAPCANĂ",
                "color": "#2563EB"
            },
            {
                "time_max": 28.5,
                "text": "3 • TENTATIVĂ vs ACTE PREP",
                "color": "#DC2626"
            },
            {
                "time_max": 99.0,
                "text": "SOLUȚIE • SIMULATOR 100 GRILE",
                "color": "#10B981"
            }
        ],
        "tiktok_caption": "Atenție la capcanele de formulare din grilele oficiale de Barou și INM! 3 detalii care fac diferența între admis și respins. Antrenează-te pe https://lexstudio-ro.vercel.app/studio ! ⚖️🏛️ #barou #inm #drept #grile #lexstudio #romania"
    },
    {
        "topic_title": "MIT SAU REALITATE: TREBUIE SĂ TOCEȘTI TOT CODUL CIVIL?",
        "alert_badge": "MIT VS REALITATE",
        "script_speech": "Crezi că pentru a lua Baroul trebuie să memorezi mecanic fiecare articol din Codul Civil? Total fals! Grilele oficiale testează corelațiile logice dintre instituții, nu memoria brută a textului. Dacă stăpânești mecanismele răspunderii civile și excepțiile de procedură, elimini instant variantele greșite. Testează-ți raționamentul juridic pe simulatorul lexstudio-ro.vercel.app/studio!",
        "sections": [
            {
                "time_max": 6.5,
                "text": "TOCITUL vs RAȚIONAMENT",
                "color": "#EF4444"
            },
            {
                "time_max": 14.0,
                "text": "CE TESTEAZĂ GRILELE",
                "color": "#F59E0B"
            },
            {
                "time_max": 21.5,
                "text": "CORELAȚIILE DINTRE CODURI",
                "color": "#2563EB"
            },
            {
                "time_max": 27.5,
                "text": "METODA DE ELIMINARE",
                "color": "#DC2626"
            },
            {
                "time_max": 99.0,
                "text": "SOLUȚIE • ANTRENEAZĂ-TE ACUM",
                "color": "#10B981"
            }
        ],
        "tiktok_caption": "Cum se învață eficient pentru Barou și INM? De ce logica juridică bate memorarea mecanică. Descoperă pe https://lexstudio-ro.vercel.app/studio ! 📚⚖️ #inm #barou #dreptcivil #metoda #lexstudio"
    },
    {
        "topic_title": "SPEȚĂ DE PENAL: COMPLICE SAU COAUTOR?",
        "alert_badge": "SPEȚĂ DE EXAMEN",
        "script_speech": "Iată o speță clasică de drept penal: o persoană stă de șase în timp ce alta pătrunde prin efracție într-un imobil. Este complice sau coautor? La examen, mulți se grăbesc spunând complicitate! Însă dacă a existat o înțelegere prealabilă și prezența la locul faptei a asigurat succesul infracțiunii, comisia califică fapta drept coautorat! Rezolvă spețe și grile corelate pe lexstudio-ro.vercel.app/studio!",
        "sections": [
            {
                "time_max": 6.5,
                "text": "SPEȚĂ CLASICĂ DE PENAL",
                "color": "#DC2626"
            },
            {
                "time_max": 13.5,
                "text": "DILEMA CALIFICĂRII",
                "color": "#F59E0B"
            },
            {
                "time_max": 20.5,
                "text": "COAUTORAT vs COMPLICITATE",
                "color": "#2563EB"
            },
            {
                "time_max": 27.0,
                "text": "MOTIVAREA BAREMULUI",
                "color": "#DC2626"
            },
            {
                "time_max": 99.0,
                "text": "SOLUȚIE • SIMULATOR OFICIAL",
                "color": "#10B981"
            }
        ],
        "tiktok_caption": "Cum rezolvi dilema dintre coautorat și complicitate în grilele de penal? Analiza speței pe https://lexstudio-ro.vercel.app/studio ! ⚖️🔍 #dreptpenal #speta #barou #inm #lexstudio"
    },
    {
        "topic_title": "AUDIT ÎN 60 SEC: GESTIUNEA TIMPULUI LA BAROU",
        "alert_badge": "AUDIT ÎN 60 SECUNDE",
        "script_speech": "Ai patru ore pentru o sută de grile. Fă acest calcul rapid pentru a nu rămâne fără timp în examen! Pasul unu: Alocă maximum două minute per grilă la prima trecere. Pasul doi: Marchează direct pe foaia de examen grilele sigure. Pasul trei: Păstrează ultimele 30 de minute exclusiv pentru trecerea pe borderoul final. Testează-ți viteza pe simulatorul complet pe lexstudio-ro.vercel.app/studio!",
        "sections": [
            {
                "time_max": 6.5,
                "text": "STRATEGIA DE 4 ORE",
                "color": "#3B82F6"
            },
            {
                "time_max": 13.5,
                "text": "1 • MAX 2 MINUTE/GRILĂ",
                "color": "#2563EB"
            },
            {
                "time_max": 20.5,
                "text": "2 • PRIMA TRECERE",
                "color": "#F59E0B"
            },
            {
                "time_max": 27.0,
                "text": "3 • TRECERE BORDEROI",
                "color": "#DC2626"
            },
            {
                "time_max": 99.0,
                "text": "SOLUȚIE • SIMULEAZĂ 100 GRILE",
                "color": "#10B981"
            }
        ],
        "tiktok_caption": "Cum împarți cele 4 ore la examenul de admitere? Testează-ți viteza și rezistența la efort pe simulatorul https://lexstudio-ro.vercel.app/studio ! ⏱️🎯 #barou #inm #managementtimp #grile #lexstudio"
    }
]

# ── Font Loader (Windows & Linux Support) ─────────────────────────
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

# ── 1. Gemini Content Generation (4 Rotating Narrative Formats) ───
ROTATING_FORMATS = [
    {
        "id": "top3_traps",
        "name": "TOP 3 CAPCANE / GREȘELI FRECVENTE",
        "instruction": (
            "FORMATUL 1: TOP 3 CAPCANE / GREȘELI FRECVENTE. "
            "Structură: Începe cu un Hook alert (primele 4 secunde) despre pericole sau greșeli majore. "
            "Urmează 3 puncte numerotate Unu / Doi / Trei (solide, concise, cu impact direct) "
            "și un îndemn final de testare pe https://lexstudio-ro.vercel.app/studio."
        ),
        "section_structure": "Secțiunea 1 (problemă #DC2626), Punctul 1 (#2563EB), Punctul 2 (#D97706), Punctul 3 (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "myth_vs_reality",
        "name": "MIT VS. REALITATE / ADEVĂRAT SAU FALS",
        "instruction": (
            "FORMATUL 2: MIT VS. REALITATE / ADEVĂRAT SAU FALS. "
            "Structură: Începe cu o întrebare provocatoare sau un mit larg răspândit ('Crezi că...? Total fals!'). "
            "Explică de ce este greșit ce crede majoritatea, oferă perspectiva corectă "
            "și un îndemn final de verificare pe https://lexstudio-ro.vercel.app/studio."
        ),
        "section_structure": "Secțiunea 1 (titlu mit #EF4444), De ce e fals (#F59E0B), Realitatea corectă (#2563EB), Regula de aur (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "case_study",
        "name": "STUDIU DE CAZ / SITUAȚIE REALĂ CONCRETĂ",
        "instruction": (
            "FORMATUL 3: STUDIU DE CAZ / SITUAȚIE CONCRETĂ. "
            "Structură: Începe cu o dilemă practică concretă ('Ce faci dacă te confrunți cu...?'). "
            "Prezintă greșeala tipică pe care o fac oamenii, pasul salvator sau soluția corectă "
            "și îndemnul de a rezolva pe https://lexstudio-ro.vercel.app/studio."
        ),
        "section_structure": "Secțiunea 1 (dilemă #DC2626), Greșeala comună (#F59E0B), Soluția pas cu pas (#2563EB), Concluzie (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "quick_audit",
        "name": "GHID RAPID / AUDIT ÎN 60 DE SECUNDE",
        "instruction": (
            "FORMATUL 4: GHID RAPID / TEST DE VERIFICARE ÎN 60 SECUNDE. "
            "Structură: Începe cu 'Fă acest test rapid în 3 pași înainte să...'. "
            "Prezintă pasul 1, pasul 2 și regula decisivă (pasul 3), "
            "urmat de îndemnul de verificare pe https://lexstudio-ro.vercel.app/studio."
        ),
        "section_structure": "Secțiunea 1 (titlu test #3B82F6), Pasul 1 (#2563EB), Pasul 2 (#F59E0B), Pasul 3 (#DC2626), CTA final (#10B981)."
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
        f"Ești scenaristul oficial pentru conținutul video scurt (TikTok / Reels) al platformei profesionale Lex Studio (https://lexstudio-ro.vercel.app/studio) - pregătire pentru admiterea în profesiile juridice din România: Barou (avocatură), INM (magistratură - judecători și procurori), admitere Drept, notariat. Simulator 100 grile oficiale, antrenament pe 5 materii (Civil, Procedură Civilă, Penal, Procedură Penală, OEPA) și corelare instantă cu articolele din coduri.\n\n"
        f"NORME OBLIGATORII PRIVIND LIMBA ROMÂNĂ (DOOM3 / ACADEMIA ROMÂNĂ):\n"
        f"- Folosește EXCLUSIV LIMBA ROMÂNĂ OFICIALĂ LITERARĂ, conform normelor ortografice, ortoepice și morfologice oficiale (DOOM3).\n"
        f"- Este STRICT INTERZISĂ orice greșeală de ortografie, fonetizare greșită sau tipar (de exemplu: scrie 'prestigiu', NICIODATĂ 'prestijiu'; 'succese', nu 'succesuri'; folosește diacritice corecte: ă, â, î, ș, ț).\n"
        f"- Textul trebuie să fie redactat impecabil din punct de vedere gramatical, lexical și stilistic.\n\n"
        f"Astăzi vei crea un scenariu conform acestui stil narativ obligatoriu:\n"
        f"{chosen_format['instruction']}\n\n"
        f"Ghidaj secțiuni grafice: {chosen_format['section_structure']}\n"
        f"Domenii recomandate: capcane de examen din Codul Civil sau Codul Penal, noutăți legislative, strategii de abordare a celor 100 de grile și corelarea articolelor de lege.\n\n"
        f"Scenariul trebuie să fie ultra-captivant, alert, de 25-30 de secunde (aproximativ 65-75 de cuvinte).\n"
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
        '  "tiktok_caption": "Descriere captivantă pentru TikTok incluzând linkul https://lexstudio-ro.vercel.app/studio și 4-6 hashtag-uri relevante: #drept #barou #inm #avocat #magistratura #grile #lexstudio #romania"\n'
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
# ── 2. Romanian Neural Audio (Gemini 2.5 Aoede Warm Female Voice) ───
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
    print("[2/4] Generare voce feminină fermecătoare, caldă & atractivă (Gemini Aoede)...")
    import base64
    import wave
    import time

    tts_models = [
        "gemini-3.1-flash-tts-preview",
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts"
    ]

    prompt = (
        f"""Citește cu o voce feminină deosebit de fermecătoare, caldă, sexy, atractivă, foarte melodioasă, sigură și perfect naturală în limba română următorul text de admitere la drept:

{script_text}"""
    )

    if GEMINI_API_KEY:
        for model in tts_models:
            for attempt in range(4):
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
                    res = requests.post(url, json=payload, timeout=90)
                    if res.status_code == 200:
                        data = res.json()
                        b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
                        pcm = base64.b64decode(b64)
                        
                        wav_path = os.path.join(OUTPUT_DIR, "daily_audio.wav")
                        with wave.open(wav_path, "wb") as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(24000)
                            wf.writeframes(pcm)
                            
                        duration = len(pcm) / 48000.0
                        words = compute_word_timestamps(script_text, duration)
                        print(f"✅ Voce feminină Aoede (caldă & atractivă) generată cu succes prin {model}: {len(pcm)} bytes, durată {duration:.2f}s, {len(words)} cuvinte sincronizate.")
                        return words, duration, wav_path
                    elif res.status_code in (429, 503):
                        wait_sec = 6 * (attempt + 1)
                        print(f"Modelul {model} a returnat {res.status_code} (încercarea {attempt+1}/4). Așteptare {wait_sec}s pentru cotă...")
                        time.sleep(wait_sec)
                    else:
                        print(f"Modelul {model} a returnat status {res.status_code}. Se trece la următorul model...")
                        break
                except Exception as e:
                    print(f"Avertisment generare voce cu {model} (încercarea {attempt+1}): {e}.")
                    time.sleep(5)

    # Fallback de urgență Edge-TTS optimizat pentru fluiditate și naturalețe (fără efect metalic)
    print("[Fallback de urgență] Folosire Edge-TTS cu timbru natural...")
    import edge_tts
    phonetic_map = {
        "online": "onlain", "site": "sait", "site-ul": "saitul",
        "feedback": "fidbac", "job": "giob", "AI": "A I", "BAC": "Bac"
    }
    spoken_text = script_text
    for en_word, ro_phonetic in phonetic_map.items():
        spoken_text = spoken_text.replace(en_word, ro_phonetic)

    communicate = edge_tts.Communicate(
        spoken_text,
        voice="ro-RO-AlinaNeural",
        rate="-2%",
        pitch="+2Hz",
        boundary="WordBoundary"
    )
    words = []
    audio_data = bytearray()
    orig_words = script_text.split()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            w_text = chunk["text"].strip()
            if not w_text:
                continue
            start_s = chunk["offset"] / 10_000_000.0
            dur_s = chunk["duration"] / 10_000_000.0
            words.append({"text": w_text, "start": start_s, "end": start_s + dur_s})
    fallback_audio = os.path.join(OUTPUT_DIR, "daily_audio.wav")
    with open(fallback_audio, "wb") as f:
        f.write(audio_data)
    duration = words[-1]["end"] + 0.4 if words else 30.0
    for i in range(min(len(words), len(orig_words))):
        words[i]["text"] = orig_words[i]
    return words, duration, fallback_audio


# ── 3. Dynamic Subtitles & Video Rendering ────────────────────────
def build_phrases(words):
    phrases = []
    current_phrase = []
    for w in words:
        current_phrase.append(w)
        has_punct = any(w["text"].endswith(p) for p in [".", "?", "!", ":", ";"])
        if len(current_phrase) >= 4 or (len(current_phrase) >= 2 and has_punct):
            phrases.append({
                "words": current_phrase,
                "start": current_phrase[0]["start"],
                "end": current_phrase[-1]["end"] + 0.15
            })
            current_phrase = []
    if current_phrase:
        phrases.append({
            "words": current_phrase,
            "start": current_phrase[0]["start"],
            "end": current_phrase[-1]["end"] + 0.2
        })
    return phrases

def render_video(scenario, words, total_duration, audio_path):
    print("[3/4] Randare cadre video 1080x1920 și codare FFmpeg x264...")
    width, height = 1080, 1920
    fps = 30
    total_frames = int(total_duration * fps)
    phrases = build_phrases(words)
    sections = scenario.get("sections", [])
    
    # Base background gradient (Deep luxury midnight slate with subtle royal amber aura)
    base_bg = Image.new("RGB", (width, height), "#0B0F19")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(height):
        ratio = y / height
        r = int(10 * (1 - ratio) + 16 * ratio)
        g = int(14 * (1 - ratio) + 20 * ratio)
        b = int(28 * (1 - ratio) + 36 * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Ambient rounded card in center with gold/slate border
    draw_bg.rounded_rectangle([60, 680, width - 60, 1260], radius=40, fill="#0E1626", outline="#1E293B", width=2)
    
    # Load fonts
    font_brand = get_font(36, bold=True)
    font_section = get_font(40, bold=True)
    font_word = get_font(64, bold=True)
    font_word_sm = get_font(40, bold=True)
    font_cta = get_font(34, bold=True)
    font_cta_sub = get_font(28, bold=True)
    font_disclaimer = get_font(22, bold=False)

    def get_w_font(text_str):
        if len(text_str) > 18:
            return font_word_sm
        return font_word

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-y",
        "-loglevel", "error",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "faster",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        VIDEO_PATH
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    brand_text = "LEX STUDIO • ADMITERE BAROU & INM"
    cta_main = "Pregătește-te pe lexstudio-ro.vercel.app/studio"
    cta_sub = "+ Urmărește pentru grile explicate zilnice"
    disc1 = "Platformă profesională de pregătire pentru admiterea în profesiile juridice."
    disc2 = "Simulator oficial de 100 de grile, 5 materii și conspectare instantanee pe articole de lege."
    
    def get_current_section(t):
        for sec in sections:
            if t <= sec.get("time_max", 999):
                return sec.get("text", "ADMITERE JURIDICĂ"), sec.get("color", "#F59E0B")
        return "SOLUȚIE • SIMULATOR OFICIAL 100 GRILE", "#10B981"
        
    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)
        
        # 1. Top Brand Pill
        pill_w, pill_h = 700, 68
        pill_x = (width - pill_w) // 2
        pill_y = 200
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=34, fill="#1E293B", outline="#F59E0B", width=2)
        b_box = draw.textbbox((0, 0), brand_text, font=font_brand)
        draw.text(((width - (b_box[2] - b_box[0])) // 2, pill_y + 15), brand_text, fill="#FBBF24", font=font_brand)
        
        # 2. Section Alert Box
        sec_text, sec_color = get_current_section(t)
        sec_bbox = draw.textbbox((0, 0), sec_text, font=font_section)
        sec_w = sec_bbox[2] - sec_bbox[0]
        s_pad = 28
        draw.rounded_rectangle(
            [(width - sec_w)//2 - s_pad, 315, (width + sec_w)//2 + s_pad, 385],
            radius=16,
            fill=sec_color
        )
        draw.text(((width - sec_w) // 2, 325), sec_text, fill="#FFFFFF", font=font_section)
        
        # 3. Dynamic Center Phrase & Word Highlighting
        active_phrase = None
        for p in phrases:
            if p["start"] <= t <= p["end"]:
                active_phrase = p
                break
        if not active_phrase:
            for p in phrases:
                if p["start"] > t:
                    active_phrase = p
                    break
        if not active_phrase and phrases:
            active_phrase = phrases[-1]
            
        if active_phrase:
            p_words = active_phrase["words"]
            word_boxes = [draw.textbbox((0, 0), w["text"].upper(), font=get_w_font(w["text"])) for w in p_words]
            spacing = 20
            total_w = sum(wb[2] - wb[0] for wb in word_boxes) + spacing * (len(p_words) - 1)
            
            if total_w <= width - 140:
                cur_x = (width - total_w) // 2
                cur_y = 920
                for i, w in enumerate(p_words):
                    f_cur = get_w_font(w["text"])
                    ww = word_boxes[i][2] - word_boxes[i][0]
                    wh = word_boxes[i][3] - word_boxes[i][1]
                    is_current = (w["start"] <= t <= w["end"] + 0.05)
                    if is_current:
                        draw.rounded_rectangle([cur_x - 16, cur_y - 10, cur_x + ww + 16, cur_y + wh + 10], radius=12, fill="#FACC15")
                        draw.text((cur_x, cur_y), w["text"].upper(), fill="#000000", font=f_cur)
                    else:
                        draw.text((cur_x + 2, cur_y + 2), w["text"].upper(), fill="#000000", font=f_cur)
                        draw.text((cur_x, cur_y), w["text"].upper(), fill="#FFFFFF", font=f_cur)
                    cur_x += ww + spacing
            else:
                half = len(p_words) // 2
                lines = [p_words[:half], p_words[half:]]
                cur_y = 860
                for line in lines:
                    line_boxes = [draw.textbbox((0, 0), w["text"].upper(), font=get_w_font(w["text"])) for w in line]
                    line_w = sum(b[2] - b[0] for b in line_boxes) + spacing * (len(line) - 1)
                    cur_x = (width - line_w) // 2
                    for i, w in enumerate(line):
                        f_cur = get_w_font(w["text"])
                        ww = line_boxes[i][2] - line_boxes[i][0]
                        wh = line_boxes[i][3] - line_boxes[i][1]
                        is_current = (w["start"] <= t <= w["end"] + 0.05)
                        if is_current:
                            draw.rounded_rectangle([cur_x - 16, cur_y - 10, cur_x + ww + 16, cur_y + wh + 10], radius=12, fill="#FACC15")
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#000000", font=f_cur)
                        else:
                            draw.text((cur_x + 2, cur_y + 2), w["text"].upper(), fill="#000000", font=f_cur)
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#FFFFFF", font=f_cur)
                        cur_x += ww + spacing
                    cur_y += 120

        # 4. Progress bar
        progress = min(1.0, t / total_duration)
        bar_left, bar_right = 80, width - 80
        bar_y = 1560
        draw.rounded_rectangle([bar_left, bar_y, bar_right, bar_y + 12], radius=6, fill="#1E293B")
        fill_w = int(bar_left + (bar_right - bar_left) * progress)
        if fill_w > bar_left + 6:
            draw.rounded_rectangle([bar_left, bar_y, fill_w, bar_y + 12], radius=6, fill="#F59E0B")
            
        # 5. Call To Action
        c1_box = draw.textbbox((0, 0), cta_main, font=font_cta)
        c2_box = draw.textbbox((0, 0), cta_sub, font=font_cta_sub)
        draw.text(((width - (c1_box[2] - c1_box[0])) // 2, 1620), cta_main, fill="#FBBF24", font=font_cta)
        draw.text(((width - (c2_box[2] - c2_box[0])) // 2, 1680), cta_sub, fill="#94A3B8", font=font_cta_sub)
        
        # 6. Micro Disclaimer
        d1_box = draw.textbbox((0, 0), disc1, font=font_disclaimer)
        d2_box = draw.textbbox((0, 0), disc2, font=font_disclaimer)
        draw.text(((width - (d1_box[2] - d1_box[0])) // 2, 1770), disc1, fill="#64748B", font=font_disclaimer)
        draw.text(((width - (d2_box[2] - d2_box[0])) // 2, 1805), disc2, fill="#64748B", font=font_disclaimer)
        
        proc.stdin.write(frame.tobytes())
        if frame_idx % 200 == 0:
            print(f"Progres randare: {(frame_idx / total_frames)*100:.1f}%...")
            
    proc.stdin.close()
    stderr_text = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    proc.wait()
    if proc.returncode != 0:
        print("Eroare FFmpeg:", stderr_text)
        return False
    print(f"✅ Video randat cu succes: {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH)/(1024*1024):.2f} MB)")
    return True

# ── 4. Dispatch Video to Telegram ─────────────────────────────────
def dispatch_to_telegram(scenario, duration):
    print("[4/4] Trimitere videoclip și descriere către Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Atenție: Lipsesc credențialele Telegram.")
        return False

    title = scenario.get("topic_title", "Capcană Examen Barou & INM")
    caption_txt = scenario.get("tiktok_caption", "Pregătește-te pe simulatorul https://lexstudio-ro.vercel.app/studio !")
    
    tg_caption = (
        f"⚖️ <b>[LEX STUDIO TIKTOK DAILY]</b>\n\n"
        f"📌 <b>Subiect:</b> {title}\n"
        f"⏱ <b>Durată:</b> {duration:.0f}s | Format 9:16 (1080x1920)\n\n"
        f"📋 <b>Atinge textul din caseta de mai jos</b> <i>(se copiază automat în clipboard pe telefon):</i>\n\n"
        f"<code>{caption_txt}</code>\n\n"
        f"👉 <i>Apasă pe video ➔ Salvează / Descarcă ➔ Lipește descrierea direct în TikTok / Reels!</i>"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(VIDEO_PATH, "rb") as vf:
        files = {"video": ("lex_studio_tiktok.mp4", vf, "video/mp4")}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": tg_caption,
            "parse_mode": "HTML",
            "supports_streaming": True
        }
        res = requests.post(url, data=data, files=files, timeout=90)
        
    res_json = res.json()
    if res_json.get("ok"):
        print("✅ Videoclipul Lex Studio a fost expediat cu succes pe Telegram!")
        return True
    else:
        print(f"❌ Eroare Telegram: {res_json.get('description')}")
        return False

# ── Main Entrypoint ───────────────────────────────────────────────
async def main():
    scenario = generate_scenario_with_gemini()
    words, duration, audio_path = await generate_audio_and_timestamps(scenario["script_speech"])
    success = render_video(scenario, words, duration, audio_path)
    if success:
        dispatch_to_telegram(scenario, duration)

if __name__ == "__main__":
    asyncio.run(main())
