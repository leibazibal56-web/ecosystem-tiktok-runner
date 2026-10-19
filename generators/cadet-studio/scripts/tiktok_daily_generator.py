# -*- coding: utf-8 -*-
"""
CADET STUDIO - Generator Complet Video TikTok & Reels (9:16 MP4)
Admitere MAI & MApN (Academia de Poliție, Școala Câmpina/Cluj, Academii Militare)
- Generează voce neurală în limba română (Gemini TTS / Edge-TTS) cu timestamp-uri pe cuvinte.
- Randează cadre video verticale 1080x1920 cu subtitrări animate dinamice și design militar/tactic.
- Encodează video MP4 cu FFmpeg și îl expediază automat pe TELEGRAM prin sendVideo!
"""

import os
import sys
import json
import time
import random
import asyncio
from datetime import datetime
import subprocess
import requests
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Credențiale & Configurație ────────────────────────────────────
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "8867321650").strip()
GEMINI_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
APP_URL = os.getenv("APP_URL") or "https://cadet-studio-admitere-mai-mapn.vercel.app"

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "video-generator"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "cadet_audio.wav")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "cadet_tiktok.mp4")

# ── Font Loader (Compatibil Windows & Linux) ───────────────────────
def get_font(size, bold=True):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf",
        "arialbd.ttf"
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

# ── Subiecte Virale cu Structură de Cadre ──────────────────────────
TIKTOK_SCENARIOS = [
    {
        "topic_title": "ADMITERE 2026: POLIȚIE (MAI) SAU ACADEMII MILITARE (MAPN)?",
        "alert_badge": "🎖️ ADMITERE MAI & MAPN 2026",
        "script_speech": "Vrei o carieră de ofițer sau subofițer în 2026? Atenție la diferențele majore dintre MAI și MApN! La Poliție și Jandarmerie dai probă la Legislație, Română DOOM3, Istorie și traseu aplicativ cu 12 obstacole. La Academiile Militare MApN, cum ar fi ATM Ferdinand I, AFT Sibiu sau AFA Brașov, susții probe scrise la Matematică, Fizică și Engleză! Nu le confunda! Pe CadetStudio ai simulatoare oficiale dedicate atât pentru MAI, cât și pentru MApN. Antrenează-te inteligent pe cadet-studio-admitere-mai-mapn.vercel.app!",
        "sections": [
            {"time_max": 5.5, "text": "🎖️ MAI SAU MAPN ÎN 2026?", "color": "#F59E0B"},
            {"time_max": 12.5, "text": "1 • MAI: LEGISLAȚIE & TRASEU", "color": "#2563EB"},
            {"time_max": 20.0, "text": "2 • MAPN: ATM, AFT & AFA", "color": "#10B981"},
            {"time_max": 26.5, "text": "3 • MATEMATICĂ & FIZICĂ MAPN", "color": "#DC2626"},
            {"time_max": 99.0, "text": "🛡️ SIMULATOR CADET STUDIO", "color": "#10B981"}
        ],
        "tiktok_caption": "🎖️ Poliție (MAI) sau Academii Militare (MApN)? Află diferențele exacte de probe scrise și sportive pentru admiterea 2026! Rezolvă grilele oficiale pe https://cadet-studio-admitere-mai-mapn.vercel.app ! 🚓⚔️ #cadetstudio #academiadepolitie #mapn #atmferdinand #aftsibiu #afabrasov #campina #politia #armata"
    },
    {
        "topic_title": "CAPCANE LA ADMITEREA ÎN ACADEMIILE MILITARE MAPN",
        "alert_badge": "⚔️ ACADEMII MILITARE MAPN",
        "script_speech": "Visezi la Academia Tehnică Militară Ferdinand I, Forțele Terestre Sibiu sau Aviație la Brașov? Punctajul la Matematică și Fizică face diferența la sutimi între admiși la buget și respinși! Subiectele de tip grilă la Algebră și Analiză conțin capcane subtile la limite de șiruri și matrici parametrice. Pe lângă scris, proba sportivă MApN cere rezistență maximă la alergarea de două mii de metri. Exersează grilele parametrice ATM și baremele sportive pe cadet-studio-admitere-mai-mapn.vercel.app!",
        "sections": [
            {"time_max": 5.5, "text": "⚔️ ADMITERE ACADEMII MAPN", "color": "#10B981"},
            {"time_max": 12.5, "text": "1 • ATM FERDINAND I: MATEMATICĂ", "color": "#2563EB"},
            {"time_max": 20.0, "text": "2 • ALGEBRĂ & ANALIZĂ PARAMETRICĂ", "color": "#F59E0B"},
            {"time_max": 26.5, "text": "3 • ALERGARE 2000M BAREM SPORTIV", "color": "#DC2626"},
            {"time_max": 99.0, "text": "🎖️ BANCA DE GRILE MAPN PE CADET", "color": "#10B981"}
        ],
        "tiktok_caption": "⚔️ Vrei la ATM Ferdinand I, AFT Sibiu sau AFA Brașov? Nu pierde admiterea la sutimi! Pregătește-te pe motorul parametric MApN și baremele sportive: https://cadet-studio-admitere-mai-mapn.vercel.app ! 🇷🇴🪖 #mapn #academiatehnicamilitara #atmferdinand #aftsibiu #afabrasov #anmb #cadetstudio #admitere2026"
    },
    {
        "topic_title": "TOP 3 CAPCANE LA ADMITEREA ÎN POLIȚIE (CÂMPINA & CLUJ)",
        "alert_badge": "👮‍♂️ ADMITERE POLIȚIE MAI 2026",
        "script_speech": "Vrei să intri la Academia de Poliție sau la Școlile de Agenți Câmpina și Cluj? Peste 40% dintre candidați pică proba teoretică din cauza a trei capcane majore! Unu: la Legislație MAI se confundă uzul de forță cu somația legală. Doi: la Română, verbele defective și acordul atributului pronominal triază masiv notele. Trei: la Istorie, cronologia tratatelor din secolul 19 face diferența la sutimi. Nu învăța la întâmplare! Antrenează-te pe simulatorul oficial cadet-studio-admitere-mai-mapn.vercel.app!",
        "sections": [
            {"time_max": 5.5, "text": "👮‍♂️ ADMITERE POLIȚIE 2026", "color": "#F59E0B"},
            {"time_max": 12.5, "text": "1 • CAPCANA LEGISLAȚIEI MAI", "color": "#2563EB"},
            {"time_max": 20.0, "text": "2 • ROMÂNĂ: VERBE DEFECTIVE", "color": "#DC2626"},
            {"time_max": 26.5, "text": "3 • CRONOLOGIE ISTORIE SEC. XIX", "color": "#F59E0B"},
            {"time_max": 99.0, "text": "🛡️ SIMULATOR CADET STUDIO", "color": "#10B981"}
        ],
        "tiktok_caption": "🎖️ Dai admiterea la Poliție sau Jandarmerie în 2026? Află cele 3 capcane din care se pierd cele mai multe puncte la proba scrisă! Rezolvă grilele oficiale pe https://cadet-studio-admitere-mai-mapn.vercel.app ! 🚓📚 #cadetstudio #academiadepolitie #scoaladepolitie #campina #politia #mapn #admitere2026"
    },
    {
        "topic_title": "TRASEUL SPORTIV MAI (12 OBSTACOLE) VS PROBA MAPN",
        "alert_badge": "🏃 PROBE SPORTIVE MAI & MAPN",
        "script_speech": "Proba fizică elimină anual sute de candidați la MAI și MApN! La MAI ai traseul practic-aplicativ cu 12 obstacole contra cronometru: săritura în lungime, gardurile, labirintul și transportul manechinului de 60 de kilograme. La MApN ai traseu utilitar aplicativ combinat cu alergare de rezistență de două mii de metri! Greșeala fatală este lipsa de ritm și penalizările la obstacole. Vezi simularea 3D a traseului și calculează-ți timpul oficial pe cadet-studio-admitere-mai-mapn.vercel.app!",
        "sections": [
            {"time_max": 5.5, "text": "🏃 BAREME SPORTIVE OFICIALE", "color": "#10B981"},
            {"time_max": 12.5, "text": "1 • MAI: 12 OBSTACOLE & MANECHIN", "color": "#2563EB"},
            {"time_max": 20.0, "text": "2 • MAPN: REZISTENȚĂ 2000 METRI", "color": "#F59E0B"},
            {"time_max": 26.5, "text": "3 • EVITĂ PENALIZĂRILE DE TIMP!", "color": "#DC2626"},
            {"time_max": 99.0, "text": "⏱️ CALCULATOR DE TRASEU CADET", "color": "#10B981"}
        ],
        "tiktok_caption": "🏃 Cum iei punctaj maxim la traseul sportiv MAI și alergarea de rezistență MApN? Vezi ghidul obstacolelor și calculatorul de barem: https://cadet-studio-admitere-mai-mapn.vercel.app ! ⏱️🏅 #traseusportiv #baremsportiv #academiadepolitie #campina #mapn #admitere2026 #cadetstudio"
    },
    {
        "topic_title": "CUM IEI AVIZUL PSIHOLOGIC APT LA MAI ȘI MAPN",
        "alert_badge": "🧠 TESTARE PSIHOLOGICĂ MAI & MAPN",
        "script_speech": "Testarea psihologică este prima mare barieră la admiterea în MAI și MApN! Peste 30% dintre candidați sunt declarați inapt fără să înțeleagă de ce. Capcana numărul unu: Scala de Minciună. Dacă încerci să pari perfect, algoritmul te depistează instantaneu ca nesincer! La MApN se testează în plus viteza de reacție și orientarea spațială sub presiune. Pe CadetStudio ai simulatorul complet cu 600 de itemi și raport instant APT sau INAPT. Testează-te acum pe cadet-studio-admitere-mai-mapn.vercel.app!",
        "sections": [
            {"time_max": 5.5, "text": "🧠 TEST PSIHOLOGIC MAI & MAPN", "color": "#8B5CF6"},
            {"time_max": 12.5, "text": "1 • CAPCANA SCALEI DE MINCIUNĂ", "color": "#DC2626"},
            {"time_max": 20.0, "text": "2 • PROBE DE REACȚIE & ORIENTARE", "color": "#2563EB"},
            {"time_max": 26.5, "text": "3 • RAPORT OFICIAL APT / INAPT", "color": "#10B981"},
            {"time_max": 99.0, "text": "🛡️ SIMULATOR PSIHOLOGIC CADET", "color": "#8B5CF6"}
        ],
        "tiktok_caption": "🧠 Dai testul psihologic pentru Poliție sau Academii Militare MApN? Află cum să eviți capcana scalei de minciună și cum iei avizul APT: https://cadet-studio-admitere-mai-mapn.vercel.app ! 📑🎯 #testpsihologic #avizapt #academiadepolitie #campina #mapn #atmferdinand #cadetstudio"
    },
    {
        "topic_title": "TRUCURI LEGISLAȚIE MAI & LIMBĂ STRĂINĂ MAPN",
        "alert_badge": "⚖️ LEGISLAȚIE & LIMBI STRĂINE",
        "script_speech": "La admiterea MAI, Legile 218 și 360 au grile formulate cu dublu înțeles! Dacă o variantă conține cuvintele întotdeauna sau fără excepție, în nouăzeci la sută din cazuri este o capcană falsă. Iar la Academiile Militare MApN, proba la Limba Engleză testează vocabular tehnic militar și structuri gramaticale avansate. Stăpânește ambele materii dintr-un singur loc! Exersează peste 16.000 de grile oficiale explicate pas cu pas pe cadet-studio-admitere-mai-mapn.vercel.app!",
        "sections": [
            {"time_max": 5.5, "text": "⚖️ TRUCURI GRILE MAI & MAPN", "color": "#2563EB"},
            {"time_max": 12.5, "text": "1 • LEGISLAȚIE MAI: STATUT & 218", "color": "#F59E0B"},
            {"time_max": 20.0, "text": "2 • ENGLEZĂ MAPN: VOCABULAR TEHNIC", "color": "#10B981"},
            {"time_max": 26.5, "text": "3 • REGULA EXCEPȚIEI LA GRILE", "color": "#DC2626"},
            {"time_max": 99.0, "text": "🎖️ 16.000+ GRILE PE CADET STUDIO", "color": "#2563EB"}
        ],
        "tiktok_caption": "⚖️ Cum rezolvi grilele de Legislație MAI și Engleză MApN fără să pici în capcane? Antrenează-te pe simulatorul complet: https://cadet-studio-admitere-mai-mapn.vercel.app ! 📚👮‍♂️🪖 #legislatiemai #englezamilitara #academiadepolitie #mapn #admitere2026 #cadetstudio"
    }
]

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
    scale = (total_duration - 0.4) / max(total_w, 1)
    
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

# ── Generare Voce & Timestamp-uri (Gemini Aoede / Edge-TTS AlinaNeural) ─────────────
async def generate_voice_and_timed_words(script_text):
    print("[1/3] Generare voce feminină clară, fermă, sigură și atractivă...")
    import base64
    import wave

    # 1. Încercare prioritară: Gemini Aoede (Voce dinamică, caldă și energică)
    if GEMINI_KEY and not GEMINI_KEY.startswith("AQ.placeholder"):
        tts_models = [
            "gemini-2.5-flash-preview-tts",
            "gemini-2.5-pro-preview-tts",
            "gemini-3.1-flash-tts-preview"
        ]
        prompt = (
            f"Citește cu o voce feminină clară, motivantă, atractivă, sigură, "
            f"fermecătoare și energică, perfect naturală în limba română, "
            f"următorul ghid de pregătire pentru admiterea în Poliție și Academiile Militare:\n\n{script_text}"
        )
        for model in tts_models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
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
                res = requests.post(url, json=payload, timeout=40)
                if res.status_code == 200:
                    data = res.json()
                    b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
                    pcm = base64.b64decode(b64)
                    with wave.open(AUDIO_PATH, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(24000)
                        wf.writeframes(pcm)
                    duration = len(pcm) / 48000.0
                    words = compute_word_timestamps(script_text, duration)
                    print(f"✅ Voce Aoede generată prin Gemini TTS! Durată: {duration:.2f}s.")
                    return words, duration, AUDIO_PATH
            except Exception:
                pass

    # 2. Fallback Neural: Edge-TTS AlinaNeural
    print("[Fallback Neural] Generare voce AlinaNeural cu reglaj tactic, energic și atractiv...")
    import edge_tts
    phonetic_map = {
        "online": "onlain",
        "site": "sait",
        "site-ul": "saitul",
        "feedback": "fidbac",
        "AI": "A I",
        "MAI": "M A I",
        "MApN": "M A P N",
        "ATM": "A T M",
        "AFT": "A F T",
        "AFA": "A F A",
        "ANMB": "A N M B",
        "UNAP": "U N A P",
        "IMM": "I M M",
        "DOOM3": "D O O M 3",
        "DOOM 3": "D O O M 3",
        "L-scale": "L scheil",
        "L-Scale": "L scheil",
        "cadet-studio-admitere-mai-mapn.vercel.app": "Cadet Studio punct vercel punct app"
    }
    spoken_text = script_text
    for en_word, ro_phonetic in phonetic_map.items():
        spoken_text = spoken_text.replace(en_word, ro_phonetic)

    communicate = edge_tts.Communicate(
        spoken_text,
        voice="ro-RO-AlinaNeural",
        rate="+1%",
        pitch="-1Hz",
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

    duration = words[-1]["end"] + 0.5 if words else 28.0
    for i in range(min(len(words), len(orig_words))):
        words[i]["text"] = orig_words[i]

    print(f"✅ Voce feminină AlinaNeural generată cu succes! Durată: {duration:.2f}s.")
    return words, duration, AUDIO_PATH

# ── Gruparea Cuvintelor în Fraze Scurte ────────────────────────────
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

# ── Randare Cadre & Codare Video MP4 cu FFmpeg ─────────────────────
def render_video_mp4(scenario, words, total_duration, audio_path):
    print("[2/3] Randare cadre video 1080x1920 și codare FFmpeg x264...")
    width, height = 1080, 1920
    fps = 30
    total_frames = int(total_duration * fps)
    phrases = build_phrases(words)
    sections = scenario.get("sections", [])

    # Fundal elegant Tactical Dark Navy
    base_bg = Image.new("RGB", (width, height), "#060E1A")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(height):
        ratio = y / height
        r = int(6 * (1 - ratio) + 14 * ratio)
        g = int(14 * (1 - ratio) + 28 * ratio)
        b = int(26 * (1 - ratio) + 48 * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))

    # Caseta centrală cu bordură tactică
    draw_bg.rounded_rectangle([60, 680, width - 60, 1260], radius=40, fill="#0A1628", outline="#1E3A8A", width=2)

    font_brand = get_font(36, bold=True)
    font_section = get_font(42, bold=True)
    font_word = get_font(66, bold=True)
    font_word_sm = get_font(44, bold=True)
    font_cta = get_font(34, bold=True)
    font_cta_sub = get_font(26, bold=False)

    def get_w_font(text_str):
        return font_word_sm if len(text_str) > 17 else font_word

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

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    badge_txt = scenario.get("alert_badge", "🎖️ CADET STUDIO ROMÂNIA")
    title_txt = scenario.get("topic_title", "ADMITERE POLIȚIE & MAPN")
    cta_main = "🎖️ SIMULATOR ADMITERE MAI & MAPN 2026"
    cta_sub = "cadet-studio-admitere-mai-mapn.vercel.app  •  Grile Oficiale Explicație Pas cu Pas"

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)

        # 1. Header Brand & Badge
        draw.rounded_rectangle([70, 90, width - 70, 175], radius=24, fill="#1E293B", outline="#475569", width=1)
        b_box = draw.textbbox((0, 0), badge_txt, font=font_brand)
        b_w = b_box[2] - b_box[0]
        draw.text(((width - b_w) // 2, 112), badge_txt, fill="#F59E0B", font=font_brand)

        # 2. Secțiunea Curentă
        cur_sec_text = title_txt
        cur_sec_color = "#3B82F6"
        for s in sections:
            if t <= s["time_max"]:
                cur_sec_text = s["text"]
                cur_sec_color = s.get("color", "#3B82F6")
                break

        draw.rounded_rectangle([80, 230, width - 80, 360], radius=24, fill="#0F172A", outline=cur_sec_color, width=3)
        s_box = draw.textbbox((0, 0), cur_sec_text, font=font_section)
        s_w = s_box[2] - s_box[0]
        draw.text(((width - s_w) // 2, 272), cur_sec_text, fill=cur_sec_color, font=font_section)

        # 3. Subtitrări Animate Karaoke în Caseta Centrală
        active_phrase = None
        for p in phrases:
            if p["start"] <= t <= p["end"]:
                active_phrase = p
                break

        if active_phrase:
            p_words = active_phrase["words"]
            space_w = 18
            total_phrase_w = sum(draw.textbbox((0, 0), w["text"], font=get_w_font(w["text"]))[2] - draw.textbbox((0, 0), w["text"], font=get_w_font(w["text"]))[0] for w in p_words) + space_w * (len(p_words) - 1)
            cur_x = (width - total_phrase_w) // 2
            start_y = 930

            for w in p_words:
                used_font = get_w_font(w["text"])
                w_box = draw.textbbox((0, 0), w["text"], font=used_font)
                w_w = w_box[2] - w_box[0]
                is_spoken = w["start"] <= t <= w["end"]

                if is_spoken:
                    text_fill = "#F59E0B" # Galben Tactic
                    hl_pad_x = 12
                    hl_pad_y = 8
                    draw.rounded_rectangle(
                        [cur_x - hl_pad_x, start_y - hl_pad_y, cur_x + w_w + hl_pad_x, start_y + (w_box[3] - w_box[1]) + hl_pad_y],
                        radius=12,
                        fill="#1E293B"
                    )
                else:
                    text_fill = "#94A3B8" if t < w["start"] else "#E2E8F0"

                draw.text((cur_x, start_y), w["text"], fill=text_fill, font=used_font)
                cur_x += w_w + space_w

        # 4. Call to Action Inferior
        cta_y = 1500
        cta_w, cta_h = 920, 110
        cta_x = (width - cta_w) // 2
        draw.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + cta_h], radius=24, fill="#1E3A8A", outline="#F59E0B", width=2)
        c_box = draw.textbbox((0, 0), cta_main, font=font_cta)
        draw.text(((width - (c_box[2] - c_box[0])) // 2, cta_y + 20), cta_main, fill="#FFFFFF", font=font_cta)
        cs_box = draw.textbbox((0, 0), cta_sub, font=font_cta_sub)
        draw.text(((width - (cs_box[2] - cs_box[0])) // 2, cta_y + 68), cta_sub, fill="#FCD34D", font=font_cta_sub)

        # 5. Bară de progres inferioară
        prog_w = int((t / total_duration) * width)
        draw.rectangle([0, height - 12, prog_w, height], fill="#F59E0B")

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        print("Eroare FFmpeg la codare video.")
        return False

    mb_size = os.path.getsize(VIDEO_PATH) / (1024 * 1024)
    print(f"✅ Video MP4 CADET randat cu succes: {VIDEO_PATH} ({mb_size:.2f} MB)")
    return True

# ── Trimitere Video MP4 direct pe Telegram (sendVideo) ─────────────
def dispatch_video_to_telegram(scenario, duration):
    print("[3/3] Trimitere fișier video MP4 și descriere către Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Atenție: Lipsesc credențialele Telegram.")
        return False

    title = scenario.get("topic_title", "Admitere MAI & MApN")
    caption_txt = scenario.get("tiktok_caption", "Pregătește-te pe simulatorul https://cadet-studio-admitere-mai-mapn.vercel.app !")

    tg_caption = (
        f"🎖️ <b>[CADET STUDIO - TIKTOK DAILY VIDEO]</b>\n\n"
        f"📌 <b>Subiect:</b> {title}\n"
        f"⏱ <b>Durată:</b> {duration:.0f} secunde | Format 9:16 (1080x1920)\n\n"
        f"📋 <b>Descrierea de copiat pe TikTok</b> <i>(atinge textul pentru copiere automată):</i>\n\n"
        f"<code>{caption_txt}</code>\n\n"
        f"👉 <i>Descarcă videoclipul MP4 atașat și postează-l direct pe TikTok / Instagram Reels / YouTube Shorts!</i>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(VIDEO_PATH, "rb") as vf:
        files = {"video": ("cadet_tiktok.mp4", vf, "video/mp4")}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": tg_caption,
            "parse_mode": "HTML",
            "supports_streaming": True
        }
        res = requests.post(url, data=data, files=files, timeout=120)

    res_json = res.json()
    if res_json.get("ok"):
        print("✅ Fișierul video MP4 CADET STUDIO a fost expediat cu succes pe Telegram!")
        return True
    else:
        print(f"❌ Eroare Telegram: {res_json.get('description')}")
        return False

# ── Entrypoint Asincron ───────────────────────────────────────────
async def main():
    day_idx = datetime.now().timetuple().tm_yday % len(TIKTOK_SCENARIOS)
    scenario = TIKTOK_SCENARIOS[day_idx]
    
    words, duration, audio_path = await generate_voice_and_timed_words(scenario["script_speech"])
    success = render_video_mp4(scenario, words, duration, audio_path)
    if success:
        dispatch_video_to_telegram(scenario, duration)

if __name__ == "__main__":
    asyncio.run(main())
