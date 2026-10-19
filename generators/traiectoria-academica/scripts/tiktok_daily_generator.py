# -*- coding: utf-8 -*-
"""
VocaStudio TikTok Daily Generator
- Generates 9:16 vertical video with Romanian Neural TTS and word-by-word dynamic subtitles.
- Uses Gemini 2.5 Flash / curatated fallback bank to synthesize fresh vocational guidance scenarios (Holland RIASEC, Big Five, University Selection).
- Dispatches final MP4 video and copy-paste caption directly to the admin Telegram bot.
- Runs seamlessly both locally on Windows and in GitHub Actions (Ubuntu).
"""
import os
import sys
import json
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
APP_URL = (os.getenv("APP_URL") or "https://vocastudio.vercel.app").strip()

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "video-generator"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "vocastudio_audio.wav")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "vocastudio_tiktok.mp4")

# ── Fallback Topics (Career Guidance & University Selection) ───────
FALLBACK_TOPICS = [
    {
        "topic_title": "3 GREȘELI CÂND ÎȚI ALEGI FACULTATEA",
        "alert_badge": "ALERTĂ CARIERĂ & BAC",
        "script_speech": "Ești în clasa a unsprezecea sau a douăsprezecea și nu știi ce facultate să alegi? Iată trei greșeli care distrug viitorul a mii de tineri! Unu: Alegerea după părerea părinților sau a prietenilor. Doi: Alegerea unei facultăți doar pentru prestigiu, fără să-ți placă domeniul. Trei: Ignorarea profilului tău psihologic Holland. Află ce carieră ți se potrivește cu adevărat pe vocastudio.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "ERORI ALEGERE FACULTATE", "color": "#EF4444"},
            {"time_max": 14.5, "text": "1 • PRESIUNEA PĂRINȚILOR", "color": "#F59E0B"},
            {"time_max": 22.5, "text": "2 • MITUL PRESTIGIULUI", "color": "#2563EB"},
            {"time_max": 28.5, "text": "3 • IGNORAREA PROFILULUI", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • TEST VOCAȚIONAL", "color": "#10B981"}
        ],
        "tiktok_caption": "Nu alege facultatea la întâmplare! 3 greșeli majore care duc la abandon universitar sau frustrare profesională. Fă testul gratuit pe https://vocastudio.vercel.app ! 🧭🎓 #facultate #bac #orientare #cariera #vocastudio #student"
    },
    {
        "topic_title": "MIT SAU REALITATE: IT-UL E SINGURUL DOMENIU DE VIITOR?",
        "alert_badge": "MIT VS REALITATE",
        "script_speech": "Crezi că dacă nu faci informatică nu vei avea un salariu bun în România? Total fals! Piața muncii este suprasaturată de juniori fără experiență, în timp ce ingineria medicală, automatizările, dreptul comercial și managementul sustenabilității oferă venituri excelente și stabilitate. Secretul este să-ți aliniezi talentele native cu cererea reală din economie. Descoperă harta carierei tale pe vocastudio.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "MITUL IT-ULUI EXCLUSIV", "color": "#EF4444"},
            {"time_max": 14.0, "text": "SATURAREA LA JUNIORI", "color": "#F59E0B"},
            {"time_max": 21.5, "text": "DOMENIILE ÎN PLINĂ CREȘTERE", "color": "#2563EB"},
            {"time_max": 27.5, "text": "ALINIERE CU VOCAȚIA TA", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • HARTA CARIEREI", "color": "#10B981"}
        ],
        "tiktok_caption": "Este programarea singura opțiune de carieră bine plătită? Iată ce caută companiile de top în 2026. Găsește-ți vocația pe https://vocastudio.vercel.app ! 💼🚀 #cariera #salariu #joburi #studenti #vocastudio"
    },
    {
        "topic_title": "CE FACI DACĂ URĂȘTI FACULTATEA PE CARE AI ÎNCEPUT-O?",
        "alert_badge": "STUDIU DE CAZ ACADEMIC",
        "script_speech": "Ai intrat la facultate și simți din primul semestru că nu este deloc locul tău? Iată planul de salvare în trei pași! Pasul unu: Nu renunța impulsiv fără o diagnoză clară. Identifică dacă problema este materia sau modul de predare. Pasul doi: Verifică opțiunile de transfer și echivalare a creditelor europene. Pasul trei: Fă o evaluare psihometrică obiectivă pentru a stabili noua traiectorie. Redefinește-ți parcursul pe vocastudio.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "BLOCAT LA FACULTATE?", "color": "#DC2626"},
            {"time_max": 13.5, "text": "1 • MATERIE vs PROFESORI", "color": "#F59E0B"},
            {"time_max": 20.5, "text": "2 • TRANSFER & ECHIVALARE", "color": "#2563EB"},
            {"time_max": 27.0, "text": "3 • PSIHOMETRIE OBIECTIVĂ", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • REORIENTARE COMPLETĂ", "color": "#10B981"}
        ],
        "tiktok_caption": "Te simți blocat la o facultate care nu te reprezintă? Nu ești singurul! Pașii concreți pentru o reorientare de succes. https://vocastudio.vercel.app 🧭🔄 #facultate #studenti #orientareprofesionala #vocastudio"
    },
    {
        "topic_title": "TEST RAPID ÎN 60 SEC: CE TIP DE PERSONALITATE AI?",
        "alert_badge": "TEST VOCAȚIONAL 60 SEC",
        "script_speech": "Ești un profil investigativ, artistic, antreprenorial sau social? Fă acest test rapid în trei întrebări! Unu: Preferi să rezolvi probleme abstracte sau să lucrezi direct cu oamenii? Doi: Îți place să construiești strategii sau să creezi concepte vizuale? Trei: Cum iei deciziile: bazat pe date reci sau pe empatie? Descoperă compatibilitatea ta exactă cu peste două sute de facultăți pe vocastudio.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "TESTUL RIASEC ÎN 60 SEC", "color": "#3B82F6"},
            {"time_max": 13.5, "text": "1 • DATE vs OAMENI", "color": "#2563EB"},
            {"time_max": 20.5, "text": "2 • STRATEGIE vs CREAȚIE", "color": "#F59E0B"},
            {"time_max": 27.0, "text": "3 • LOGICĂ vs EMPATIE", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • POTRIVIRE FACULTĂȚI", "color": "#10B981"}
        ],
        "tiktok_caption": "Investigativ, antreprenorial sau artistic? Află ce profil vocațional Holland ai și ce facultăți ți se potrivesc mănușă! Testează pe https://vocastudio.vercel.app ! 🎯📊 #psihologie #riasec #vocational #facultate #vocastudio"
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

# ── Gemini Content Synthesis ──────────────────────────────────────
def generate_scenario_with_gemini():
    day_idx = random.randint(0, len(FALLBACK_TOPICS) - 1)
    chosen_fallback = FALLBACK_TOPICS[day_idx]

    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("AQ.placeholder"):
        return chosen_fallback

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        system_prompt = (
            "Ești un expert de top în orientare vocațională, psihometrie educațională (RIASEC, Big Five) și admitere universitară în România pentru platforma VocaStudio. "
            "Generează un scenariu video scurt pentru TikTok (25-28 secunde rostit alert, aproximativ 65-75 cuvinte). "
            "Trebuie să fie extrem de util pentru elevi de liceu, părinți și studenți. "
            "La final, include îndemnul: 'Descoperă-ți vocația pe vocastudio.vercel.app!'\n\n"
            "NORME OBLIGATORII PRIVIND LIMBA ROMÂNĂ (DOOM3 / ACADEMIA ROMÂNĂ):\n"
            "- Folosește EXCLUSIV LIMBA ROMÂNĂ OFICIALĂ LITERARĂ, conform normelor ortografice, ortoepice și de punctuație oficiale (DOOM3).\n"
            "- Este STRICT INTERZISĂ orice greșeală de ortografie, fonetizare sau tipar (de exemplu: scrie 'prestigiu', NICIODATĂ 'prestijiu'; 'succese', nu 'succesuri'; folosește diacritice corecte: ă, â, î, ș, ț).\n"
            "- Textul trebuie să fie redactat impecabil din punct de vedere gramatical, lexical și stilistic.\n\n"
            "Răspunde STRICT cu un obiect JSON valid având cheile:\n"
            "topic_title: titlu scurt cu majuscule (max 6 cuvinte)\n"
            "alert_badge: badge scurt (max 3 cuvinte)\n"
            "script_speech: textul exact rostit de voce în limba română literară corectă (fără ghilimele sau paranteze)\n"
            "sections: listă cu 5 secțiuni având time_max (secunde crescătoare până la 99.0), text (text cadru scris corect), color (hex color de alertă: #EF4444, #F59E0B, #2563EB, #DC2626, #10B981)\n"
            "tiktok_caption: descrierea pentru postare, max 150 caractere cu link https://vocastudio.vercel.app și 5 hashtag-uri relevante."
        )
        payload = {
            "contents": [{"parts": [{"text": system_prompt}]}],
            "generationConfig": {"temperature": 0.7, "response_mime_type": "application/json"}
        }
        res = requests.post(url, json=payload, timeout=20)
        if res.status_code == 200:
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            scenario = json.loads(raw_text)
            if all(k in scenario for k in ["topic_title", "script_speech", "sections", "tiktok_caption"]):
                print("✅ Scenariu generat proaspăt cu Gemini 2.5 Flash pentru VocaStudio!")
                return scenario
    except Exception as e:
        print(f"Atenție: Fallback la baza curatată ({e}).")

    return chosen_fallback

# ── 2. Romanian & English Neural Audio (Gemini Aoede Female Voice) ───
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
    print("[1/3] Generare voce feminină plăcută, caldă & melodioasă (Gemini Aoede)...")
    import base64
    import wave
    import time

    tts_models = [
        "gemini-3.1-flash-tts-preview",
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts"
    ]

    prompt = (
        f"""Citește cu o voce feminină deosebit de plăcută, caldă, empatică, melodioasă, sigură și perfect naturală în limba română și engleză (cu pronunție corectă a termenilor academici și de carieră în română și engleză) următorul text de orientare vocațională:

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
                        
                        wav_path = AUDIO_PATH
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

    # Fallback de urgență Edge-TTS optimizat pentru fluiditate, naturalețe și dicție bilingvă română-engleză
    print("[Fallback de urgență] Folosire Edge-TTS cu timbru feminin cald și dicționar fonetic bilingv...")
    import edge_tts
    import re
    phonetic_map = {
        # Platform & Domains
        "vocastudio.vercel.app": "voca studio punct vercel punct app",
        "VocaStudio": "VocaStudio",
        # English career, academic & tech terms
        "feedback-ul": "fidbacul", "feedback": "fidbac",
        "job-urile": "gioburile", "job-uri": "gioburi", "joburi": "gioburi", "job-ul": "giobul", "job": "giob",
        "career": "carier", "coaching": "cociing", "coach": "coci",
        "soft skills": "soft schils", "hard skills": "hard schils", "skills": "schils",
        "IT-ul": "Ai Ti-ul", "IT-ului": "Ai Ti-ului", "IT": "Ai Ti",
        "HR-ul": "Haș Er-ul", "HR": "Haș Er",
        "managementul": "menegimentul", "management": "menegiment",
        "marketingul": "marchetingul", "marketing": "marcheting",
        "business-ul": "biznisul", "business": "biznis",
        "designul": "dizainul", "design": "dizain", "designer": "dizainer",
        "developers": "developerz", "developer": "developer",
        "freelancing": "frilensing", "freelancer": "frilenser", "freelance": "frilens",
        "internship-uri": "internșipuri", "internshipuri": "internșipuri", "internship": "internșip",
        "juniori": "giuniori", "junior": "giunior", "senior": "senior",
        "networking": "netuorching", "AI": "A I", "CV-ul": "Ce Ve-ul", "CV": "Ce Ve",
        "online": "onlain", "offline": "oflain", "site-ul": "saitul", "site": "sait",
        "Big Five": "Big Faiv", "Holland": "Holand", "RIASEC": "Ria-sec",
        "full-time": "ful taim", "part-time": "part taim", "work-life balance": "uorc laif balans", "remote": "rimout",
        # Romanian acronyms
        "BAC-ul": "Bacul", "BAC-ului": "Bacului", "BAC": "Bac",
        "SNSPA": "S N S P A", "ASE": "A S E", "UPB": "U P B", "UMF": "U M F", "UB": "U B", "UAIC": "U A I C"
    }

    spoken_text = script_text
    sorted_replacements = sorted(phonetic_map.items(), key=lambda x: len(x[0]), reverse=True)
    for en_word, ro_phonetic in sorted_replacements:
        pattern = r'\b' + re.escape(en_word) + r'\b'
        spoken_text = re.sub(pattern, ro_phonetic, spoken_text, flags=re.IGNORECASE)

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

    with open(AUDIO_PATH, "wb") as f:
        f.write(audio_data)

    duration = words[-1]["end"] + 0.4 if words else 28.0
    for i in range(min(len(words), len(orig_words))):
        words[i]["text"] = orig_words[i]

    print(f"Fallback audio salvat: {len(audio_data)} bytes, {len(words)} cuvinte, durată: {duration:.2f}s.")
    return words, duration, AUDIO_PATH

# ── Subtitles Grouping ────────────────────────────────────────────
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
                "end": current_phrase[-1]["end"] + 0.2
            })
            current_phrase = []
    if current_phrase:
        phrases.append({
            "words": current_phrase,
            "start": current_phrase[0]["start"],
            "end": current_phrase[-1]["end"] + 0.25
        })
    return phrases

# ── Render 9:16 Video with FFmpeg ─────────────────────────────────
def render_video(scenario, words, total_duration, audio_path):
    print("[2/3] Randare cadre video 1080x1920 și codare FFmpeg libx264...")
    width, height = 1080, 1920
    fps = 30
    total_frames = int(total_duration * fps)
    phrases = build_phrases(words)
    sections = scenario.get("sections", [])

    base_bg = Image.new("RGB", (width, height), "#0B1120")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(height):
        ratio = y / height
        r = int(11 * (1 - ratio) + 15 * ratio)
        g = int(17 * (1 - ratio) + 23 * ratio)
        b = int(32 * (1 - ratio) + 42 * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))

    draw_bg.rounded_rectangle([60, 680, width - 60, 1260], radius=40, fill="#111827", outline="#3B82F6", width=2)

    font_brand = get_font(34, bold=True)
    font_section = get_font(40, bold=True)
    font_word = get_font(64, bold=True)
    font_word_sm = get_font(44, bold=True)
    font_cta = get_font(34, bold=True)
    font_cta_sub = get_font(26, bold=False)
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

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    brand_text = "🎓 TRAIECTORIA ACADEMICĂ • GHID FACULTĂȚI"
    cta_main = "Descoperă facultatea ta pe vocastudio.vercel.app"
    cta_sub = "Urmărește pentru ghiduri de admitere și carieră"
    disc1 = "Evaluare educațională orientativă bazată pe modelele psihometrice RIASEC & Big Five."
    disc2 = "Platformă autonomă de consiliere educațională și potrivire cu facultățile din România."

    def get_current_section(t):
        for sec in sections:
            if t <= sec.get("time_max", 999):
                return sec.get("text", "ORIENTARE VOCAȚIONALĂ"), sec.get("color", "#3B82F6")
        return "SOLUȚIE • EVALUARE VOCAȚIONALĂ", "#10B981"

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)

        # 1. Antet Brand Pill
        pill_w, pill_h = 760, 68
        pill_x = (width - pill_w) // 2
        pill_y = 190
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=34, fill="#1E293B", outline="#6366F1", width=2)
        b_box = draw.textbbox((0, 0), brand_text, font=font_brand)
        draw.text(((width - (b_box[2] - b_box[0])) // 2, pill_y + 14), brand_text, fill="#A5B4FC", font=font_brand)

        # 2. Badge de Secțiune
        sec_text, sec_color = get_current_section(t)
        sec_bbox = draw.textbbox((0, 0), sec_text, font=font_section)
        sec_w = sec_bbox[2] - sec_bbox[0]
        s_pad = 30
        draw.rounded_rectangle(
            [(width - sec_w) // 2 - s_pad, 310, (width + sec_w) // 2 + s_pad, 385],
            radius=18,
            fill=sec_color
        )
        draw.text(((width - sec_w) // 2, 322), sec_text, fill="#FFFFFF", font=font_section)

        # 3. Subtitrări Dinamice
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
            phrase_words = active_phrase["words"]
            full_str = " ".join([w["text"] for w in phrase_words])
            used_font = font_word_sm if len(full_str) > 17 else font_word

            word_bboxes = [draw.textbbox((0, 0), w["text"], font=used_font) for w in phrase_words]
            word_widths = [b[2] - b[0] for b in word_bboxes]
            space_w = draw.textbbox((0, 0), " ", font=used_font)[2]
            total_phrase_w = sum(word_widths) + (len(phrase_words) - 1) * space_w

            start_x = (width - total_phrase_w) // 2
            start_y = 930
            cur_x = start_x

            for w, w_w in zip(phrase_words, word_widths):
                is_active = (w["start"] <= t <= w["end"] + 0.05)
                if is_active:
                    pad_x, pad_y = 10, 8
                    draw.rounded_rectangle(
                        [cur_x - pad_x, start_y - pad_y, cur_x + w_w + pad_x, start_y + 80 + pad_y],
                        radius=12,
                        fill="#FACC15"
                    )
                    draw.text((cur_x, start_y), w["text"], fill="#0F172A", font=used_font)
                else:
                    draw.text((cur_x + 2, start_y + 2), w["text"], fill="#000000", font=used_font)
                    draw.text((cur_x, start_y), w["text"], fill="#FFFFFF", font=used_font)
                cur_x += w_w + space_w

        # 4. Progress bar
        progress = min(1.0, t / total_duration)
        bar_left, bar_right = 80, width - 80
        bar_y = 1560
        draw.rounded_rectangle([bar_left, bar_y, bar_right, bar_y + 12], radius=6, fill="#1E293B")
        fill_w = int(bar_left + (bar_right - bar_left) * progress)
        if fill_w > bar_left + 6:
            draw.rounded_rectangle([bar_left, bar_y, fill_w, bar_y + 12], radius=6, fill="#10B981")

        # 5. Call to Action
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
    print(f"✅ Video VocaStudio randat cu succes: {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH)/(1024*1024):.2f} MB)")
    return True

# ── 4. Dispatch Video to Telegram ─────────────────────────────────
def dispatch_to_telegram(scenario, duration):
    print("[3/3] Trimitere videoclip și descriere către Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Atenție: Lipsesc credențialele Telegram.")
        return False

    title = scenario.get("topic_title", "Ghid Vocațional & Admitere Facultate")
    caption_txt = scenario.get("tiktok_caption", "Descoperă-ți vocația pe https://vocastudio.vercel.app !")

    tg_caption = (
        f"🎓 <b>[TRAIECTORIA ACADEMICĂ TIKTOK DAILY]</b>\n\n"
        f"📌 <b>Subiect:</b> {title}\n"
        f"⏱ <b>Durată:</b> {duration:.0f}s | Format 9:16 (1080x1920)\n\n"
        f"📋 <b>Atinge textul din caseta de mai jos</b> <i>(se copiază automat în clipboard pe telefon):</i>\n\n"
        f"<code>{caption_txt}</code>\n\n"
        f"👉 <i>Apasă pe video ➔ Salvează / Descarcă ➔ Lipește descrierea direct în TikTok / Reels!</i>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(VIDEO_PATH, "rb") as vf:
        files = {"video": ("vocastudio_tiktok.mp4", vf, "video/mp4")}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": tg_caption,
            "parse_mode": "HTML",
            "supports_streaming": True
        }
        res = requests.post(url, data=data, files=files, timeout=90)

    res_json = res.json()
    if res_json.get("ok"):
        print("✅ Videoclipul VocaStudio a fost expediat cu succes pe Telegram!")
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
