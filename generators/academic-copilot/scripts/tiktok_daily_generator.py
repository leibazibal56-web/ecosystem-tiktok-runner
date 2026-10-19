# -*- coding: utf-8 -*-
"""
Academic Copilot TikTok Daily Generator
- Generates 9:16 vertical videos with Gemini 2.5 Flash TTS warm female voice (Aoede) & dynamic subtitles.
- Uses Gemini 2.5 Flash to synthesize fresh academic advice for university students (Licență, Dizertație, Cercetare).
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
VIDEO_PATH = os.path.join(OUTPUT_DIR, "academic_copilot_tiktok.mp4")

# ── Fallback Topics (Academic Thesis & Research Traps) ────────────
FALLBACK_TOPICS = [
    {
        "topic_title": "3 GREȘELI LA LICENȚĂ CARE TE POT PICA",
        "alert_badge": "LICENȚĂ & DIZERTAȚIE",
        "script_speech": "Ești pe ultima sută de metri cu lucrarea de licență sau dizertație? Iată trei greșeli care enervează comisia la culme! Unu: Bibliografie învechită. Dacă peste jumătate din surse sunt mai vechi de zece ani, comisia va depuncta stadiul cunoașterii. Doi: Citare incorectă. Nu amesteca formatul A P A cu I S O șase sute nouăzeci. Trei: Lipsa ipotezelor clare. Structurează și validează lucrarea gratuit pe academic-copilot.vercel.app!",
        "sections": [
            {
                "time_max": 6.5,
                "text": "ERORI CRITICE LICENȚĂ",
                "color": "#EF4444"
            },
            {
                "time_max": 14.5,
                "text": "1 • BIBLIOGRAFIE VECHE",
                "color": "#F59E0B"
            },
            {
                "time_max": 22.5,
                "text": "2 • AMESTEC DE STANDARDE",
                "color": "#06B6D4"
            },
            {
                "time_max": 28.5,
                "text": "3 • IPOTEZE FORMALE",
                "color": "#3B82F6"
            },
            {
                "time_max": 99.0,
                "text": "SOLUȚIE • ASISTENT ACADEMIC",
                "color": "#10B981"
            }
        ],
        "tiktok_caption": "Nu lăsa greșelile de formă să-ți strice nota la licență sau dizertație! 3 erori care enervează comisia. Validează-ți lucrarea pe https://academic-copilot.vercel.app ! 🎓📚 #licenta #dizertatie #studenti #facultate #academiccopilot"
    },
    {
        "topic_title": "MIT SAU REALITATE: PARAFRAZAREA FĂRĂ CITARE E PLAGIAT?",
        "alert_badge": "MIT VS REALITATE",
        "script_speech": "Crezi că dacă schimbi câteva cuvinte și nu pui ghilimele, softul antiplagiat nu te prinde? Total fals! Preluarea unei idei sau structuri fără a cita autorul original este considerată plagiat de conținut de orice comisie universitară. Secretul este parafrazarea autentică însoțită mereu de referința sursei. Organizează-ți bibliografia și citările corecte pe academic-copilot.vercel.app!",
        "sections": [
            {
                "time_max": 6.5,
                "text": "CAPCANA PARAFRAZĂRII",
                "color": "#EF4444"
            },
            {
                "time_max": 14.0,
                "text": "CE VERIFICĂ SOFTUL",
                "color": "#F59E0B"
            },
            {
                "time_max": 21.5,
                "text": "PLAGIATUL DE CONȚINUT",
                "color": "#DC2626"
            },
            {
                "time_max": 27.5,
                "text": "REGULA CITĂRII CORECTE",
                "color": "#3B82F6"
            },
            {
                "time_max": 99.0,
                "text": "SOLUȚIE • CITARE AUTOMATĂ",
                "color": "#10B981"
            }
        ],
        "tiktok_caption": "Atenție la mitul parafrazării! Chiar și ideile rescrise trebuie citate corect conform standardelor. Folosește asistentul tău pe https://academic-copilot.vercel.app ! 📖🔍 #antiplagiat #licenta #cercetare #student #academiccopilot"
    },
    {
        "topic_title": "PROFESORUL COORDONATOR ȚI-A RESPINS CAPITOLUL 2?",
        "alert_badge": "STUDIU DE CAZ ACADEMIC",
        "script_speech": "Profesorul ți-a returnat capitolul doi spunând că este doar o înșiruire de citate fără spirit critic? Iată cum îl transformi în douăzeci și patru de ore! Pasul unu: Nu descrie fiecare autor izolat, ci creează o matrice comparativă de sinteză. Pasul doi: Identifică limitele studiilor actuale. Pasul trei: Conectează teoria direct cu cercetarea ta practică. Generează matrice de sinteză pe academic-copilot.vercel.app!",
        "sections": [
            {
                "time_max": 6.5,
                "text": "CAPITOLUL 2 RESPINS?",
                "color": "#DC2626"
            },
            {
                "time_max": 13.5,
                "text": "MATRICE COMPARATIVĂ",
                "color": "#F59E0B"
            },
            {
                "time_max": 20.5,
                "text": "ANALIZĂ CRITICĂ",
                "color": "#06B6D4"
            },
            {
                "time_max": 27.0,
                "text": "CONEXIUNEA CU PRACTICA",
                "color": "#3B82F6"
            },
            {
                "time_max": 99.0,
                "text": "SOLUȚIE • SINTEZĂ ACADEMICĂ",
                "color": "#10B981"
            }
        ],
        "tiktok_caption": "Cum transformi stadiul cunoașterii într-o analiză apreciată de comisie? Pașii concreți pentru un capitol impecabil! https://academic-copilot.vercel.app 📊🎓 #licenta #dizertatie #coordonator #studiudecaz #academiccopilot"
    },
    {
        "topic_title": "AUDIT ÎN 60 SEC: BIBLIOGRAFIA TA RESPECTĂ APA 7?",
        "alert_badge": "AUDIT ÎN 60 SECUNDE",
        "script_speech": "Predai lucrarea săptămâna aceasta? Fă acest test rapid în 60 de secunde pentru bibliografie! Pasul unu: Toate sursele citate în text se regăsesc exact în lista finală? Pasul doi: Articolele științifice au link D O I valid? Pasul trei: Respectă ordinea alfabetică strictă fără numerotare manuală greșită? Validează și formatează bibliografia în câteva secunde pe academic-copilot.vercel.app!",
        "sections": [
            {
                "time_max": 6.5,
                "text": "TESTUL BIBLIOGRAFIEI APA 7",
                "color": "#3B82F6"
            },
            {
                "time_max": 13.5,
                "text": "1 • CORESPONDENȚĂ ÎN TEXT",
                "color": "#06B6D4"
            },
            {
                "time_max": 20.5,
                "text": "2 • IDENTIFICATOR DOI VALID",
                "color": "#F59E0B"
            },
            {
                "time_max": 27.0,
                "text": "3 • ORDONARE ALFABETICĂ",
                "color": "#DC2626"
            },
            {
                "time_max": 99.0,
                "text": "SOLUȚIE • FORMATOR AUTOMAT",
                "color": "#10B981"
            }
        ],
        "tiktok_caption": "Nu lăsa formatarea bibliografiei să-ți scadă nota finală! Testează în 60 de secunde pe https://academic-copilot.vercel.app ! 📚✨ #bibliografie #apa7 #licenta #dizertatie #academiccopilot"
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
            "și un îndemn final de testare pe https://academic-copilot.vercel.app."
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
            "și un îndemn final de verificare pe https://academic-copilot.vercel.app."
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
            "și îndemnul de a rezolva pe https://academic-copilot.vercel.app."
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
            "urmat de îndemnul de verificare pe https://academic-copilot.vercel.app."
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
        f"Ești scenaristul oficial pentru conținutul video scurt (TikTok / Reels) al platformei universitare Academic Copilot (https://academic-copilot.vercel.app) - asistent academic dedicat studenților și masteranzilor (ASE, Drept, Medicină, Politehnică, Litere) pentru redactarea licenței și dizertației, căutare bibliografică automată prin OpenAlex, matrice de sinteză, citare automată (APA 7, ISO 690, Harvard, IEEE) și ghidare împotriva plagiatului.\n\n"
        f"NORME OBLIGATORII PRIVIND LIMBA ROMÂNĂ (DOOM3 / ACADEMIA ROMÂNĂ):\n"
        f"- Folosește EXCLUSIV LIMBA ROMÂNĂ OFICIALĂ LITERARĂ, conform normelor ortografice, ortoepice și morfologice oficiale (DOOM3).\n"
        f"- Este STRICT INTERZISĂ orice greșeală de ortografie, fonetizare greșită sau tipar (de exemplu: scrie 'prestigiu', NICIODATĂ 'prestijiu'; 'succese', nu 'succesuri'; folosește diacritice corecte: ă, â, î, ș, ț).\n"
        f"- Textul trebuie să fie redactat impecabil din punct de vedere gramatical, lexical și stilistic.\n\n"
        f"Astăzi vei crea un scenariu conform acestui stil narativ obligatoriu:\n"
        f"{chosen_format['instruction']}\n\n"
        f"Ghidaj secțiuni grafice: {chosen_format['section_structure']}\n"
        f"Domenii recomandate: teme legate de licență, dizertație, metodologie de cercetare, căutare surse academice, citare corectă APA/ISO și evitarea plagiatului.\n\n"
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
        '  "tiktok_caption": "Descriere captivantă pentru TikTok incluzând linkul https://academic-copilot.vercel.app și 4-6 hashtag-uri relevante: #licenta #dizertatie #facultate #studenti #cercetare #apa7 #academiccopilot #romania"\n'
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
        f"""Citește cu o voce feminină deosebit de fermecătoare, caldă, sexy, atractivă, foarte melodioasă, sigură și perfect naturală în limba română următorul text universitar de cercetare:

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
    
    # Base background gradient (Deep academic midnight slate with emerald tint)
    base_bg = Image.new("RGB", (width, height), "#0B111E")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(height):
        ratio = y / height
        r = int(9 * (1 - ratio) + 15 * ratio)
        g = int(17 * (1 - ratio) + 26 * ratio)
        b = int(30 * (1 - ratio) + 42 * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Ambient rounded card in center with subtle emerald border
    draw_bg.rounded_rectangle([60, 680, width - 60, 1260], radius=40, fill="#0F172A", outline="#1E293B", width=2)
    
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
    brand_text = "ACADEMIC COPILOT • LICENȚĂ & DIZERTAȚIE"
    cta_main = "Cercetează pe academic-copilot.vercel.app"
    cta_sub = "+ Urmărește pentru sfaturi de licență și cercetare"
    disc1 = "Asistent inteligent de cercetare academică și analiză bibliografică."
    disc2 = "Ghidare metodologică, citări corecte APA / ISO 690 și integritate academică."
    
    def get_current_section(t):
        for sec in sections:
            if t <= sec.get("time_max", 999):
                return sec.get("text", "CERCETARE ACADEMICĂ"), sec.get("color", "#10B981")
        return "SOLUȚIE • ASISTENT ACADEMIC", "#10B981"
        
    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)
        
        # 1. Top Brand Pill
        pill_w, pill_h = 760, 68
        pill_x = (width - pill_w) // 2
        pill_y = 200
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=34, fill="#1E293B", outline="#10B981", width=2)
        b_box = draw.textbbox((0, 0), brand_text, font=font_brand)
        draw.text(((width - (b_box[2] - b_box[0])) // 2, pill_y + 15), brand_text, fill="#34D399", font=font_brand)
        
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
            draw.rounded_rectangle([bar_left, bar_y, fill_w, bar_y + 12], radius=6, fill="#10B981")
            
        # 5. Call To Action
        c1_box = draw.textbbox((0, 0), cta_main, font=font_cta)
        c2_box = draw.textbbox((0, 0), cta_sub, font=font_cta_sub)
        draw.text(((width - (c1_box[2] - c1_box[0])) // 2, 1620), cta_main, fill="#34D399", font=font_cta)
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

    title = scenario.get("topic_title", "Ghid Lucrare de Licență & Dizertație")
    caption_txt = scenario.get("tiktok_caption", "Structurează-ți lucrarea pe https://academic-copilot.vercel.app !")
    
    tg_caption = (
        f"🎓 <b>[ACADEMIC COPILOT TIKTOK DAILY]</b>\n\n"
        f"📌 <b>Subiect:</b> {title}\n"
        f"⏱ <b>Durată:</b> {duration:.0f}s | Format 9:16 (1080x1920)\n\n"
        f"📋 <b>Atinge textul din caseta de mai jos</b> <i>(se copiază automat în clipboard pe telefon):</i>\n\n"
        f"<code>{caption_txt}</code>\n\n"
        f"👉 <i>Apasă pe video ➔ Salvează / Descarcă ➔ Lipește descrierea direct în TikTok / Reels!</i>"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(VIDEO_PATH, "rb") as vf:
        files = {"video": ("academic_copilot_tiktok.mp4", vf, "video/mp4")}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": tg_caption,
            "parse_mode": "HTML",
            "supports_streaming": True
        }
        res = requests.post(url, data=data, files=files, timeout=90)
        
    res_json = res.json()
    if res_json.get("ok"):
        print("✅ Videoclipul Academic Copilot a fost expediat cu succes pe Telegram!")
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
