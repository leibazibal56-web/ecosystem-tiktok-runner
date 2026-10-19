# -*- coding: utf-8 -*-
"""
LexSinteză - TikTok Daily Video Generator
Generare automată de conținut video vertical 1080x1920 (TikTok / Reels / Shorts)
Aplicația: https://lex-sinteza.vercel.app
"""
import os
import sys
import json
import time
import random
import asyncio
import subprocess
import requests
import edge_tts
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
VIDEO_PATH = os.path.join(OUTPUT_DIR, "lexsinteza_tiktok.mp4")

# ── 4 Fallback Topics (One for each Rotating Narrative Format) ─────
FALLBACK_TOPICS = [
    {
        "topic_title": "3 CAPCANE DOCTRINALE: NULITATEA ÎN CIVIL",
        "alert_badge": "DOCTRINĂ CIVILĂ",
        "script_speech": "Te pregătești pentru admiterea la Barou sau INM? Iată trei capcane clasice din tratatele de drept civil! Unu: Nulitatea relativă nu poate fi invocată de instanță din oficiu, oricât de gravă pare neregula. Doi: Confirmarea expresă sau tacită a actului anulează dreptul de a cere nulitatea relativă. Trei: Prescripția de trei ani curge diferit în caz de violență sau dol. Consultă matricele comparative și sintezele pe lex-sinteza.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "CAPCANE LA NULITATE", "color": "#DC2626"},
            {"time_max": 14.5, "text": "1 • INVOCARE DIN OFICIU", "color": "#2563EB"},
            {"time_max": 22.5, "text": "2 • CONFIRMAREA ACTULUI", "color": "#D97706"},
            {"time_max": 28.5, "text": "3 • CURGEREA PRESCRIPȚIEI", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • MATRICE COMPARATIVĂ", "color": "#10B981"}
        ],
        "tiktok_caption": "Stăpânești distincțiile fine dintre nulitatea absolută și cea relativă? 3 capcane doctrinale din tratatele Boroi și Bîrsan. Învață logic pe https://lex-sinteza.vercel.app ! ⚖️🏛️ #lexsinteza #dreptcivil #nulitate #barou #inm #romania"
    },
    {
        "topic_title": "MIT SAU REALITATE: TOATE TERMENELE SE CALCULEAZĂ PE ZILE LIBERE?",
        "alert_badge": "MIT VS REALITATE",
        "script_speech": "Crezi că orice termen de procedură se calculează după regula zilelor libere? Total fals! În timp ce Codul de Procedură Civilă aplică regula zilelor libere conform Articolului 181, Codul de Procedură Penală impune regula zilelor pline conform Articolului 269. O confuzie de o singură zi îți poate anula calea de atac! Folosește calculatorul automat de termene procedurale pe lex-sinteza.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "MITUL TERMENELOR PROCEDURALE", "color": "#EF4444"},
            {"time_max": 14.0, "text": "CIVIL: ZILE LIBERE (ART 181)", "color": "#F59E0B"},
            {"time_max": 21.5, "text": "PENAL: ZILE PLINE (ART 269)", "color": "#2563EB"},
            {"time_max": 27.5, "text": "RISCUL DECĂDERII", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • CALCULATOR TERMENE", "color": "#10B981"}
        ],
        "tiktok_caption": "Atenție maximă la calculul termenelor procedurale! Zile libere în Civil vs. zile pline în Penal. Calculează exact și evită decăderea pe https://lex-sinteza.vercel.app ! ⏱️⚖️ #lexsinteza #proceduracivila #procedurapenala #termene #barou #inm"
    },
    {
        "topic_title": "ORDINEA EXCEPȚIILOR: ARBORELE DECIZIONAL ART 248 CPC",
        "alert_badge": "ARBORE DECIZIONAL",
        "script_speech": "Cum soluționează instanța excepțiile când pârâtul invocă simultan necompetența, prescripția și lipsa de interes? Iată regula de aur din Articolul 248! Instanța se pronunță mai întâi asupra excepțiilor de procedură și abia apoi asupra celor de fond. Astfel, necompetența este analizată prioritar, înainte de orice discuție pe fond sau prescripție. Explorează schemele logice și arborii decizionali pe lex-sinteza.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "CONFLICT DE EXCEPȚII?", "color": "#DC2626"},
            {"time_max": 13.5, "text": "REGULA ART. 248 CPC", "color": "#F59E0B"},
            {"time_max": 20.5, "text": "PROCEDURĂ vs FOND", "color": "#2563EB"},
            {"time_max": 27.0, "text": "PRIORITATEA NECOMPETENȚEI", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • ARBORI DECIZIONALI", "color": "#10B981"}
        ],
        "tiktok_caption": "Cum rezolvi ordinea de soluționare a excepțiilor procesuale? Schema logică conform Art. 248 CPC explicată pe https://lex-sinteza.vercel.app ! 🔀⚖️ #lexsinteza #exceptiiprocesuale #dpc #boroi #magistratura #barou"
    },
    {
        "topic_title": "AUDIT ÎN 60 SEC: CALCULUL TERMENULUI DE APEL",
        "alert_badge": "AUDIT ÎN 60 SECUNDE",
        "script_speech": "Ai primit o hotărâre civilă și vrei să calculezi termenul de apel de treizeci de zile? Fă acest test rapid în trei pași! Pasul unu: Nu număra ziua comunicării și nici ziua împlinirii termenului, fiind un termen pe zile libere. Pasul doi: Dacă ultima zi este o zi nelucrătoare sau sărbătoare legală, termenul se prorogă automat până la sfârșitul primei zile lucrătoare. Pasul trei: Verifică data ștampilei poștei. Calculează termenele instant pe lex-sinteza.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "TESTUL TERMENULUI DE APEL", "color": "#3B82F6"},
            {"time_max": 13.5, "text": "1 • REGULA ZILELOR LIBERE", "color": "#2563EB"},
            {"time_max": 20.5, "text": "2 • PROROGARE WEEKEND / SĂRBĂTORI", "color": "#F59E0B"},
            {"time_max": 27.0, "text": "3 • ȘTAMPILA POȘTEI", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • CALCULEAZĂ PE SITE", "color": "#10B981"}
        ],
        "tiktok_caption": "Cum calculezi fără greșeală termenul de apel de 30 de zile în civil? Testul rapid de 60 de secunde cu regulile de prorogare. Verifică pe https://lex-sinteza.vercel.app ! 📅⚖️ #lexsinteza #apel #termeneprocedurale #proceduracivila #drept"
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
            "Structură: Începe cu un Hook alert (primele 4 secunde) despre capcane teoretice și doctrinare majore. "
            "Urmează 3 puncte numerotate Unu / Doi / Trei (solide, concise, cu impact direct) "
            "și un îndemn final de testare pe https://lex-sinteza.vercel.app."
        ),
        "section_structure": "Secțiunea 1 (problemă #DC2626), Punctul 1 (#2563EB), Punctul 2 (#D97706), Punctul 3 (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "myth_vs_reality",
        "name": "MIT VS. REALITATE / ADEVĂRAT SAU FALS",
        "instruction": (
            "FORMATUL 2: MIT VS. REALITATE / ADEVĂRAT SAU FALS. "
            "Structură: Începe cu o întrebare provocatoare sau un mit larg răspândit ('Crezi că...? Total fals!'). "
            "Explică de ce este greșit ce crede majoritatea, oferă perspectiva doctrinară corectă "
            "și un îndemn final de verificare pe https://lex-sinteza.vercel.app."
        ),
        "section_structure": "Secțiunea 1 (titlu mit #EF4444), De ce e fals (#F59E0B), Realitatea corectă (#2563EB), Regula de aur (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "case_study",
        "name": "STUDIU DE CAZ / ARBORE DECIZIONAL",
        "instruction": (
            "FORMATUL 3: STUDIU DE CAZ / SITUAȚIE CONCRETĂ & ARBORE DECIZIONAL. "
            "Structură: Începe cu o dilemă practică sau calificare juridică ('Ce faci dacă te confrunți cu...?'). "
            "Prezintă greșeala tipică pe care o fac candidații, pasul corect de rezolvare conform legii "
            "și îndemnul de a rezolva pe https://lex-sinteza.vercel.app."
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
            "urmat de îndemnul de verificare pe https://lex-sinteza.vercel.app."
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
        f"Ești scenaristul oficial pentru conținutul video scurt (TikTok / Reels) al platformei LexSinteză (https://lex-sinteza.vercel.app) - Arhitectura Minții Juridice: platformă de pregătire teoretică, matrice de sinteze comparative în 10 puncte, scheme logice, arbori decizionali și calcul procedural (Art. 181 CPC vs Art. 269 CPP) pentru Magistratură (INM), Avocatură (Barou), Notariat (INR) și Consilieri Juridici.\n\n"
        f"NORME OBLIGATORII PRIVIND LIMBA ROMÂNĂ (DOOM3 / ACADEMIA ROMÂNĂ):\n"
        f"- Folosește EXCLUSIV LIMBA ROMÂNĂ OFICIALĂ LITERARĂ, conform normelor ortografice, ortoepice și morfologice oficiale (DOOM3).\n"
        f"- Este STRICT INTERZISĂ orice greșeală de ortografie, fonetizare greșită sau tipar (de exemplu: scrie 'prestigiu', NICIODATĂ 'prestijiu'; 'succese', nu 'succesuri'; folosește diacritice corecte: ă, â, î, ș, ț).\n"
        f"- Textul trebuie să fie redactat impecabil din punct de vedere gramatical, lexical și stilistic.\n\n"
        f"Astăzi vei crea un scenariu conform acestui stil narativ obligatoriu:\n"
        f"{chosen_format['instruction']}\n\n"
        f"Ghidaj secțiuni grafice: {chosen_format['section_structure']}\n"
        f"Domenii recomandate: sinteze comparative Boroi / Streteanu / Bîrsan, calcul termene procedurale CPC vs CPP, ordinea soluționării excepțiilor Art. 248 CPC, succesiuni și devoluțiune notarială, nulitate, prescripție, delapidare vs furt vs abuz în serviciu.\n\n"
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
        '  "tiktok_caption": "Descriere captivantă pentru TikTok incluzând linkul https://lex-sinteza.vercel.app și 4-6 hashtag-uri relevante: #lexsinteza #drept #barou #inm #magistratura #notariat #teorie #romania"\n'
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

# ── 2. Romanian Neural Audio (Gemini Aoede Suave & Natural Voice) ──
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
    print("[2/4] Generare voce feminină suavă, caldă & atractivă (Gemini Aoede)...")
    import base64
    import wave
    import time

    tts_models = [
        "gemini-2.5-flash-preview-tts",
        "gemini-3.1-flash-tts-preview",
        "gemini-2.5-pro-preview-tts"
    ]

    prompt = (
        f"""Citește cu o voce feminină deosebit de suavă, fermecătoare, caldă, sexy, atractivă, foarte melodioasă, sigură și perfect naturală în limba română următorul text de teorie și sinteză juridică:

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
                        print(f"✅ Voce feminină Aoede (suavă & atractivă) generată cu succes prin {model}: {len(pcm)} bytes, durată {duration:.2f}s, {len(words)} cuvinte sincronizate.")
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
        "CPC": "C P C", "CPP": "C P P", "INM": "I N M", "INR": "I N R",
        "RIL": "Ril", "HP": "H P", "CCR": "C C R"
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
        if len(current_phrase) >= 4 or any(w["text"].endswith(p) for p in [".", ",", "?", "!", ":", ";"]):
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
    
    # Base background gradient (Deep Night Blue to Imperial Navy)
    base_bg = Image.new("RGB", (width, height), "#0A0E1A")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(height):
        ratio = y / height
        r = int(10 * (1 - ratio) + 8 * ratio)
        g = int(18 * (1 - ratio) + 14 * ratio)
        b = int(34 * (1 - ratio) + 24 * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Ambient rounded card in center
    draw_bg.rounded_rectangle([60, 680, width - 60, 1260], radius=40, fill="#0F172A", outline="#1E293B", width=2)
    
    # Load fonts
    font_brand = get_font(34, bold=True)
    font_section = get_font(40, bold=True)
    font_word = get_font(64, bold=True)
    font_cta = get_font(34, bold=True)
    font_cta_sub = get_font(28, bold=True)
    font_disclaimer = get_font(22, bold=False)

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
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    brand_text = "LEXSINTEZĂ  •  ARHITECTURA MINȚII JURIDICE"
    cta_main = "Sinteze și arbori decizionali pe lex-sinteza.vercel.app"
    cta_sub = "+ Urmărește pentru pregătire teoretică de elită"
    disc1 = "Informații cu caracter educativ și teoretic."
    disc2 = "Conform Legii 51/1995, LexSinteză oferă asistență teoretică educațională."
    
    def get_current_section(t):
        for sec in sections:
            if t <= sec.get("time_max", 999):
                return sec.get("text", "SINTEZĂ DOCTRINARĂ"), sec.get("color", "#DC2626")
        return "SOLUȚIE • ARHITECTURA MINȚII", "#10B981"
        
    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)
        
        # 1. Top Brand Pill
        pill_w, pill_h = 760, 68
        pill_x = (width - pill_w) // 2
        pill_y = 200
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=34, fill="#1E293B", outline="#38BDF8", width=2)
        b_box = draw.textbbox((0, 0), brand_text, font=font_brand)
        draw.text(((width - (b_box[2] - b_box[0])) // 2, pill_y + 16), brand_text, fill="#38BDF8", font=font_brand)
        
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
            word_boxes = [draw.textbbox((0, 0), w["text"].upper(), font=font_word) for w in p_words]
            spacing = 20
            total_w = sum(wb[2] - wb[0] for wb in word_boxes) + spacing * (len(p_words) - 1)
            
            if total_w <= width - 140:
                cur_x = (width - total_w) // 2
                cur_y = 920
                for i, w in enumerate(p_words):
                    ww = word_boxes[i][2] - word_boxes[i][0]
                    wh = word_boxes[i][3] - word_boxes[i][1]
                    is_current = (w["start"] <= t <= w["end"] + 0.05)
                    if is_current:
                        draw.rounded_rectangle([cur_x - 16, cur_y - 10, cur_x + ww + 16, cur_y + wh + 10], radius=12, fill="#FACC15")
                        draw.text((cur_x, cur_y), w["text"].upper(), fill="#000000", font=font_word)
                    else:
                        draw.text((cur_x + 2, cur_y + 2), w["text"].upper(), fill="#000000", font=font_word)
                        draw.text((cur_x, cur_y), w["text"].upper(), fill="#FFFFFF", font=font_word)
                    cur_x += ww + spacing
            else:
                half = len(p_words) // 2
                lines = [p_words[:half], p_words[half:]]
                cur_y = 860
                for line in lines:
                    line_boxes = [draw.textbbox((0, 0), w["text"].upper(), font=font_word) for w in line]
                    line_w = sum(b[2] - b[0] for b in line_boxes) + spacing * (len(line) - 1)
                    cur_x = (width - line_w) // 2
                    for i, w in enumerate(line):
                        ww = line_boxes[i][2] - line_boxes[i][0]
                        wh = line_boxes[i][3] - line_boxes[i][1]
                        is_current = (w["start"] <= t <= w["end"] + 0.05)
                        if is_current:
                            draw.rounded_rectangle([cur_x - 14, cur_y - 8, cur_x + ww + 14, cur_y + wh + 8], radius=10, fill="#FACC15")
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#000000", font=font_word)
                        else:
                            draw.text((cur_x + 2, cur_y + 2), w["text"].upper(), fill="#000000", font=font_word)
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#FFFFFF", font=font_word)
                        cur_x += ww + spacing
                    cur_y += 110

        # 4. Progress Timeline Bar
        bar_w = width - 200
        bar_left = 100
        bar_y = 1520
        draw.rounded_rectangle([bar_left, bar_y, bar_left + bar_w, bar_y + 12], radius=6, fill="#334155")
        progress = min(1.0, max(0.0, t / total_duration)) if total_duration > 0 else 0
        fill_w = bar_left + int(bar_w * progress)
        if fill_w > bar_left + 6:
            draw.rounded_rectangle([bar_left, bar_y, fill_w, bar_y + 12], radius=6, fill="#10B981")
            
        # 5. Call To Action
        c1_box = draw.textbbox((0, 0), cta_main, font=font_cta)
        c2_box = draw.textbbox((0, 0), cta_sub, font=font_cta_sub)
        draw.text(((width - (c1_box[2] - c1_box[0])) // 2, 1620), cta_main, fill="#38BDF8", font=font_cta)
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

    title = scenario.get("topic_title", "Sinteză Teoretică & Calcul Procedural")
    caption_txt = scenario.get("tiktok_caption", "Aprofundează teoria juridică pe https://lex-sinteza.vercel.app !")
    
    tg_caption = (
        f"🎬 <b>[LEXSINTEZĂ TIKTOK DAILY]</b>\n\n"
        f"📌 <b>Subiect:</b> {title}\n"
        f"⏱️ <b>Durată video:</b> {duration:.1f} secunde\n\n"
        f"📋 <b>Atinge textul din caseta de mai jos</b> <i>(se copiază automat în clipboard pe telefon):</i>\n\n"
        f"<code>{caption_txt}</code>\n\n"
        f"👉 <i>Apasă pe video ➔ Salvează / Descarcă ➔ Lipește descrierea direct în TikTok / Reels!</i>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(VIDEO_PATH, "rb") as video_file:
        files = {"video": (os.path.basename(VIDEO_PATH), video_file, "video/mp4")}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": tg_caption,
            "parse_mode": "HTML",
            "supports_streaming": True
        }
        res = requests.post(url, data=data, files=files, timeout=90)
        
    res_json = res.json()
    if res_json.get("ok"):
        print("✅ Videoclipul LexSinteză a fost expediat cu succes pe Telegram!")
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
