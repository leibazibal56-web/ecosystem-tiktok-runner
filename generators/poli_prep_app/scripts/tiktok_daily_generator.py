# -*- coding: utf-8 -*-
"""
PoliPrep Pro TikTok Daily Generator
====================================
- Generează videoclipuri verticale 9:16 (1080x1920) pentru TikTok / Instagram Reels / YouTube Shorts.
- Voce feminină oficială Aoede (Google Gemini Audio TTS) – caldă, umană, melodică și atractivă.
- Fallback de înaltă fidelitate Edge-TTS (ro-RO-AlinaNeural) cu dicționar fonetic UPB.
- Subtitrări dinamice animate stil Karaoke sincronizate la nivel de cuvânt.
- Conținut axat 100% pe admiterea la Politehnica București (UNSTPB):
  * Matematică (Analiză, Algebră)
  * Fizică (Mecanică, Termodinamică, Electricitate)
  * Informatică C++ (CTI / ACS)
  * Strategii pentru proba de 180 min și baremul de 0.90p/grilă
- Expediere automată spre aprobare pe Telegram (Human-in-the-Loop) înainte de postare.
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

# ── Credențiale & Configurare ──────────────────────────────────────
GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "8867321650").strip()

OUTPUT_DIR = os.path.abspath(os.path.join(ROOT_DIR, "video-generator"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "poliprep_audio.wav")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "poliprep_tiktok.mp4")

# ── Subiecte Fallback Curate UPB ───────────────────────────────────
FALLBACK_TOPICS = [
    {
        "topic_title": "3 CAPCANE LA MATEMATICĂ LA POLITEHNICĂ",
        "alert_badge": "MATEMATICĂ ADMITERE UPB",
        "script_speech": "Dai admiterea la Politehnică anul acesta? Iată trei capcane clasice la matematică din care se pierd două puncte! Unu: La calculul integralei funcției inverse, nu te apuca să calculezi inversa explicit. Folosește formula ariei! Doi: La polinoame, rădăcinile reale se verifică mereu prin relațiile lui Viète și schema Horner. Trei: Nu uita condițiile de existență la logaritmi. Exersează cele 794 de grile oficiale rezolvate pe poliprep-upb.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "CAPCANE MATE UPB", "color": "#0284C7"},
            {"time_max": 14.0, "text": "1 • INTEGRALA INVERSEI", "color": "#6366F1"},
            {"time_max": 21.5, "text": "2 • POLINOAME & VIÈTE", "color": "#F59E0B"},
            {"time_max": 27.5, "text": "3 • DOMENIU LOGARITMI", "color": "#EF4444"},
            {"time_max": 99.0, "text": "SOLUȚIE • SIMULATOR 180 MIN", "color": "#10B981"}
        ],
        "tiktok_caption": "3 capcane clasice la examenul scris de Matematică la Politehnică! Antrenează-te pe simulatoarele oficiale de 180 minute pe https://poliprep-upb.vercel.app ! 📐🚀 #upb #politehnica #admitere2026 #matematica #acs #etti #poliprep"
    },
    {
        "topic_title": "CUM GESTIONEZI CELE 180 MINUTE LA POLI?",
        "alert_badge": "STRATEGIE EXAMEN UPB",
        "script_speech": "Ai 10 probleme și 180 de minute la admiterea la Politehnică. Cum îți împarți timpul ca să iei peste nota nouă? Pasul unu: Rezolvă în primele 40 de minute cele patru grile rapide de nivel mediu. Pasul doi: Alocă 80 de minute pentru cele cinci probleme de sinteză. Pasul trei: Păstrează ultima jumătate de oră pentru verificarea calculelor și completarea atentă a foii de răspuns optice. Testează simulatorul oficial cu cronometru pe poliprep-upb.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "TACTICA 180 MINUTE", "color": "#0284C7"},
            {"time_max": 13.5, "text": "ETAPA 1 • 40 MIN / GRILE RAPIDE", "color": "#10B981"},
            {"time_max": 21.0, "text": "ETAPA 2 • 80 MIN / PROBLEME GRELE", "color": "#F59E0B"},
            {"time_max": 27.5, "text": "ETAPA 3 • 30 MIN / FOAIA OPTICĂ", "color": "#EF4444"},
            {"time_max": 99.0, "text": "SIMULATOR CU BULINE OPTICE", "color": "#38BDF8"}
        ],
        "tiktok_caption": "Cum îți împarți cele 180 de minute la examenul scris UPB? Strategia care te duce la Buget la ACS sau ETTI! Testează pe https://poliprep-upb.vercel.app ! ⏱️🎯 #politehnica #admitereupb #bacalaureat #inginerie #simulatorupb"
    },
    {
        "topic_title": "SECRETUL RANDAMENTULUI LA FIZICĂ UPB",
        "alert_badge": "FIZICĂ CONCURS UPB",
        "script_speech": "Te sperie problemele de termodinamică la fizică pentru admitere? Iată secretul ciclului Carnot! Randamentul maxim depinde doar de temperaturile sursei calde și ale sursei reci. Niciodată de natura gazului ideal! Dacă sursa rece scade cu 50 de Kelvin, randamentul crește instantaneu. Fii atent la unitățile de măsură: transformă mereu gradele Celsius în Kelvin! Găsești rezolvările demonstrative pas cu pas pe poliprep-upb.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "TERMODINAMICĂ UPB", "color": "#F59E0B"},
            {"time_max": 14.0, "text": "RANDAMENTUL CARNOT", "color": "#0284C7"},
            {"time_max": 21.5, "text": "CAPCANA: KELVIN vs CELSIUS", "color": "#EF4444"},
            {"time_max": 27.5, "text": "UNITĂȚI ÎN SISTEM INTERNAȚIONAL", "color": "#6366F1"},
            {"time_max": 99.0, "text": "SOLUȚIE • 250+ GRILE FIZICĂ", "color": "#10B981"}
        ],
        "tiktok_caption": "Capcana randamentului Carnot la Fizică la Politehnică! Învață trucurile de concurs pe https://poliprep-upb.vercel.app ! ⚡🔬 #fizica #upb #admitere #termodinamica #politehnicabucuresti"
    },
    {
        "topic_title": "ALGORITMI PE ARBORI PENTRU ADMITERE LA CTI",
        "alert_badge": "INFORMATICĂ C++ ACS",
        "script_speech": "Dai admiterea la Calculatoare și Tehnologia Informației? Iată ce pică mereu la informatică: parcurgerile de arbori și analiza de complexitate! Reține că o căutare binară are complexitate logaritmică, dar dacă vectorul nu este sortat din start, ai greșit grila! Fii atent la valorile de frontieră și indicii de la zero la n minus unu. Exersează subiectele oficiale din 2026 pe poliprep-upb.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "INFORMATICĂ C++ CTI", "color": "#10B981"},
            {"time_max": 13.5, "text": "ARBORI & RECURSIVITATE", "color": "#0284C7"},
            {"time_max": 20.5, "text": "CAPCANA VECTORILOR NESORTAȚI", "color": "#EF4444"},
            {"time_max": 27.0, "text": "COMPLEXITATE O(LOG N)", "color": "#F59E0B"},
            {"time_max": 99.0, "text": "SOLUȚIE • GRILE OFICIALE 2026", "color": "#38BDF8"}
        ],
        "tiktok_caption": "Trucuri esențiale de Informatică C++ pentru admiterea la ACS / CTI Politehnică! Antrenează-te pe https://poliprep-upb.vercel.app ! 💻🚀 #informatica #cplusplus #acs #cti #upb #admitere2026"
    }
]

# ── Font Loader ───────────────────────────────────────────────────
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

# ── 1. Generare Scenariu prin Gemini 2.5 Flash ────────────────────
def generate_scenario_with_gemini():
    import datetime
    day_idx = datetime.datetime.now().timetuple().tm_yday % len(FALLBACK_TOPICS)
    fallback = FALLBACK_TOPICS[day_idx]
    print(f"[1/4] Solicitare scenariu nou admitere UPB prin Gemini 2.5 Flash...")

    if not GEMINI_API_KEY:
        print("Lipsă GEMINI_API_KEY. Se folosește scenariul academic de rezervă.")
        return fallback

    prompt = (
        "Ești scenaristul oficial pentru videoclipurile TikTok/Reels ale platformei educaționale PoliPrep Pro (https://poliprep-upb.vercel.app) – platforma de elită pentru admiterea la Universitatea Națională de Știință și Tehnologie Politehnica București (UNSTPB / UPB).\n"
        "Creează un scenariu ultra-captivant, alert, de 65-75 cuvinte, rostit de o voce feminină caldă, sigură și inteligentă.\n"
        "Subiecte posibile: capcane la matematică (analiză/algebră), fizică (mecanică/termo/electricitate), informatică C++ (CTI/ACS) sau sfaturi tactice pentru gestionarea celor 180 de minute de concurs și baremul de 0.90p/grilă.\n\n"
        "Returnează EXCLUSIV un obiect JSON cu structura:\n"
        "{\n"
        '  "topic_title": "TITLU ÎN MAJUSCULE (max 5 cuvinte)",\n'
        '  "alert_badge": "CATEGORIE (ex: MATEMATICĂ UPB, STRATEGIE 180 MIN, FIZICĂ CONCURS)",\n'
        '  "script_speech": "Textul rostit în limba română (65-75 cuvinte), cursiv, alert, cu cifre scrise în cuvinte (unu, doi, trei, zece, o sută optzeci), îndemnând spre https://poliprep-upb.vercel.app la final.",\n'
        '  "sections": [\n'
        '    {"time_max": 6.5, "text": "TITLU INTRODUcere", "color": "#0284C7"},\n'
        '    {"time_max": 14.0, "text": "PUNCTUL 1", "color": "#6366F1"},\n'
        '    {"time_max": 21.5, "text": "PUNCTUL 2", "color": "#F59E0B"},\n'
        '    {"time_max": 27.5, "text": "PUNCTUL 3 / CONCLUZIE", "color": "#EF4444"},\n'
        '    {"time_max": 99.0, "text": "SOLUȚIE • SIMULATOR OFICIAL", "color": "#10B981"}\n'
        '  ],\n'
        '  "tiktok_caption": "Descriere captivantă pentru TikTok incluzând https://poliprep-upb.vercel.app și 4-6 hashtag-uri: #upb #politehnica #admitere2026 #matematica #fizica #acs #etti #poliprep"\n'
        "}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "topP": 0.95}
    }
    try:
        res = requests.post(url, json=payload, timeout=40)
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
            print(f"✅ Scenariu generat cu succes prin Gemini: {parsed.get('topic_title')}")
            return parsed
        else:
            print(f"Atenție: Răspuns Gemini {res.status_code}. Se trece pe fallback.")
            return fallback
    except Exception as e:
        print(f"Atenție apel Gemini: {e}. Se trece pe fallback.")
        return fallback

# ── 2. Generare Voce Aoede (sau Fallback Neural) ───────────────────
def compute_word_timestamps(script_text, total_duration):
    words = script_text.split()
    weights = []
    for w in words:
        clean = w.rstrip(".,?!:;")
        base = max(1, len(clean))
        if any(w.endswith(p) for p in [".", "?", "!"]):
            pause = 3.2
        elif any(w.endswith(p) for p in [",", ":", ";"]):
            pause = 1.8
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
    print("[2/4] Generare voce feminină Aoede (umană, caldă, melodică & atractivă)...")
    import base64
    import wave
    import time

    tts_models = [
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts",
        "gemini-3.1-flash-tts-preview"
    ]

    tts_prompt = (
        "Citește cu o voce feminină deosebit de caldă, umană, melodică, sigură, prietenoasă și atractivă "
        "în limba română următorul ghid educațional pentru candidații la Politehnică:\n\n"
        f"{script_text}"
    )

    if GEMINI_API_KEY:
        for model in tts_models:
            for attempt in range(3):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                    payload = {
                        "contents": [{"parts": [{"text": tts_prompt}]}],
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
                        b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
                        pcm = base64.b64decode(b64)

                        wav_path = os.path.join(OUTPUT_DIR, "poliprep_audio.wav")
                        with wave.open(wav_path, "wb") as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(24000)
                            wf.writeframes(pcm)

                        duration = len(pcm) / 48000.0
                        words = compute_word_timestamps(script_text, duration)
                        print(f"✅ Voce feminină Aoede generată cu succes ({model}): {len(pcm)} bytes, durată {duration:.2f}s, {len(words)} cuvinte.")
                        return words, duration, wav_path
                    elif res.status_code in (429, 503):
                        print(f"Modelul {model} temporar ocupat ({res.status_code}). Așteptare 4s...")
                        time.sleep(4)
                    else:
                        break
                except Exception as e:
                    print(f"Atenție generare voce cu {model}: {e}")
                    time.sleep(3)

    # Fallback Edge-TTS de rezervă cu AlinaNeural și dicționar fonetic UPB
    print("[Fallback de rezervă] Generare voce prin Edge-TTS ro-RO-AlinaNeural...")
    import edge_tts
    phonetic_map = {
        "UPB": "U P B",
        "ACS": "A C S",
        "ETTI": "E T T I",
        "CTI": "C T I",
        "UNSTPB": "Politehnica București",
        "KaTeX": "CaTec",
        "site": "sait",
        "online": "onlain"
    }
    spoken = script_text
    for k, v in phonetic_map.items():
        spoken = spoken.replace(k, v)

    communicate = edge_tts.Communicate(
        spoken,
        voice="ro-RO-AlinaNeural",
        rate="-2%",
        pitch="+2Hz",
        boundary="WordBoundary"
    )

    audio_data = bytearray()
    words = []
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

    wav_fallback = os.path.join(OUTPUT_DIR, "poliprep_audio.wav")
    with open(wav_fallback, "wb") as f:
        f.write(audio_data)

    duration = words[-1]["end"] + 0.4 if words else 30.0
    for i in range(min(len(words), len(orig_words))):
        words[i]["text"] = orig_words[i]

    print(f"✅ Voce generată prin Edge-TTS fallback: {len(audio_data)} bytes, durată {duration:.2f}s.")
    return words, duration, wav_fallback

# ── 3. Subtitrare & Randare Cadre Video 1080x1920 ─────────────────
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
    print("[3/4] Randare cadre video verticale 1080x1920 și codare FFmpeg x264...")
    width, height = 1080, 1920
    fps = 30
    total_frames = int(total_duration * fps)
    phrases = build_phrases(words)
    sections = scenario.get("sections", [])

    # Gradient de fundal PoliPrep Pro (Deep Midnight Blue to Dark Slate)
    base_bg = Image.new("RGB", (width, height), "#080C16")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(height):
        ratio = y / height
        r = int(6 * (1 - ratio) + 14 * ratio)
        g = int(12 * (1 - ratio) + 24 * ratio)
        b = int(28 * (1 - ratio) + 48 * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))

    # Card ambiental central cu bordură fină
    draw_bg.rounded_rectangle([60, 680, width - 60, 1260], radius=40, fill="#0F172A", outline="#1E293B", width=2)

    # Încărcare fonturi
    font_brand = get_font(34, bold=True)
    font_section = get_font(40, bold=True)
    font_word = get_font(62, bold=True)
    font_word_sm = get_font(42, bold=True)
    font_cta = get_font(34, bold=True)
    font_cta_sub = get_font(28, bold=True)
    font_disclaimer = get_font(22, bold=False)

    def get_w_font(text_str):
        if len(text_str) > 16:
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
    brand_text = "POLIPREP PRO • ADMITERE POLITEHNICĂ UPB"
    cta_main = "https://poliprep-upb.vercel.app/"
    cta_sub = "Exersează pe https://poliprep-upb.vercel.app/ • 794 Grile UPB"
    disc1 = "Platformă de elită pentru admiterea la Universitatea Națională de Știință și Tehnologie Politehnica București."
    disc2 = "794 grile explicate, subiecte oficiale 2026 și simulare cu foaie optică • TEODORESCU O.DIANA PFA"

    def get_current_section(t):
        for sec in sections:
            if t <= sec.get("time_max", 999):
                return sec.get("text", "ADMITERE UPB 2026"), sec.get("color", "#0284C7")
        return "SOLUȚIE • SIMULATOR OFICIAL", "#10B981"

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)

        # 1. Top Brand Pill
        pill_w, pill_h = 740, 68
        pill_x = (width - pill_w) // 2
        pill_y = 190
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=34, fill="#0F172A", outline="#0284C7", width=2)
        b_box = draw.textbbox((0, 0), brand_text, font=font_brand)
        draw.text(((width - (b_box[2] - b_box[0])) // 2, pill_y + 15), brand_text, fill="#38BDF8", font=font_brand)

        # 2. Section Alert Badge
        sec_text, sec_color = get_current_section(t)
        sec_bbox = draw.textbbox((0, 0), sec_text, font=font_section)
        sec_w = sec_bbox[2] - sec_bbox[0]
        s_pad = 28
        draw.rounded_rectangle(
            [(width - sec_w)//2 - s_pad, 305, (width + sec_w)//2 + s_pad, 380],
            radius=16,
            fill=sec_color
        )
        draw.text(((width - sec_w) // 2, 317), sec_text, fill="#FFFFFF", font=font_section)

        # 3. Dynamic Center Phrase & Word-by-Word Karaoke Highlight
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
            draw.rounded_rectangle([bar_left, bar_y, fill_w, bar_y + 12], radius=6, fill="#38BDF8")

        # 5. Call To Action (Pill rotunjit elegant cu URL-ul exact)
        url_box = draw.textbbox((0, 0), cta_main, font=font_cta)
        url_w = url_box[2] - url_box[0]
        pill_pad_x = 36
        pill_pad_y = 14
        pill_x0 = (width - url_w) // 2 - pill_pad_x
        pill_y0 = 1605
        pill_x1 = (width + url_w) // 2 + pill_pad_x
        pill_y1 = pill_y0 + (url_box[3] - url_box[1]) + pill_pad_y * 2
        draw.rounded_rectangle([pill_x0, pill_y0, pill_x1, pill_y1], radius=24, fill="#0F172A", outline="#38BDF8", width=2)
        draw.text(((width - url_w) // 2, pill_y0 + pill_pad_y - 2), cta_main, fill="#38BDF8", font=font_cta)

        sub_box = draw.textbbox((0, 0), cta_sub, font=font_cta_sub)
        sub_w = sub_box[2] - sub_box[0]
        draw.text(((width - sub_w) // 2, 1695), cta_sub, fill="#94A3B8", font=font_cta_sub)

        # 6. Micro Disclaimer
        draw.text(((width - draw.textbbox((0, 0), disc1, font=font_disclaimer)[2]) // 2, 1770), disc1, fill="#64748B", font=font_disclaimer)
        draw.text(((width - draw.textbbox((0, 0), disc2, font=font_disclaimer)[2]) // 2, 1805), disc2, fill="#64748B", font=font_disclaimer)

        proc.stdin.write(frame.tobytes())
        if frame_idx % 250 == 0:
            print(f"Progres randare PoliPrep TikTok: {(frame_idx / total_frames)*100:.1f}%...")

    proc.stdin.close()
    stderr_text = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    proc.wait()
    if proc.returncode != 0:
        print("Eroare FFmpeg:", stderr_text)
        return False
    print(f"✅ Video TikTok PoliPrep randat cu succes: {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH)/(1024*1024):.2f} MB)")
    return True

# ── 4. Expediere spre Telegram (Human-in-the-Loop) ─────────────────
async def dispatch_to_telegram(scenario, duration):
    print("[4/4] Trimitere videoclip PoliPrep Pro spre aprobare pe Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Atenție: Lipsesc credențialele Telegram în mediu. Sări peste expediere.")
        return False

    from services.telegram_publisher import send_video_for_approval

    title = scenario.get("topic_title", "Capcană Admitere Politehnică UPB")
    caption_txt = scenario.get("tiktok_caption", "Pregătește-te de concurs pe https://poliprep-upb-.vercel.app !")

    result = await send_video_for_approval(
        video_path=VIDEO_PATH,
        caption=caption_txt,
        title=title,
        duration=duration,
        bot_token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID
    )

    if result.get("success"):
        print(f"✅ Videoclipul PoliPrep Pro a fost trimis cu succes pe Telegram!")
        print(f"   Message ID: {result.get('message_id')}")
        print(f"   Video ID: {result.get('video_id')}")
        print("👉 Administratorul poate apăsa [ 🚀 Publică pe TikTok ] direct în Telegram!")
        return True
    else:
        print(f"❌ Eroare expediere Telegram: {result.get('error')}")
        return False

# ── Entrypoint ────────────────────────────────────────────────────
async def main():
    scenario = generate_scenario_with_gemini()
    words, duration, audio_path = await generate_audio_and_timestamps(scenario["script_speech"])
    success = render_video(scenario, words, duration, audio_path)
    if success:
        await dispatch_to_telegram(scenario, duration)

if __name__ == "__main__":
    asyncio.run(main())
