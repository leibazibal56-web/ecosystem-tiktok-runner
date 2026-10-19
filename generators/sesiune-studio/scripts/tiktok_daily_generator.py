# -*- coding: utf-8 -*-
"""
SESIUNESTUDIO — Generator Automat Video TikTok, Instagram Reels & YouTube Shorts (9:16 MP4)
─────────────────────────────────────────────────────────────────────────────────────────────
- Generează voce neurală feminină caldă, catifelată și atractivă în limba română (Gemini TTS / Edge-TTS AlinaNeural).
- Calculează timestamp-uri precise la nivel de cuvânt pentru subtitrări dinamice animate.
- Randează cadre video verticale 1080x1920 cu design modern pentru studenți (carduri indigo/cyan, radare de catedră).
- Encodează video MP4 cu FFmpeg și îl expediază automat pe TELEGRAM prin sendVideo cu descriere gata de copy-paste!
"""

import os
import sys
import json
import time
import base64
import wave
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

# ── Credențiale & Configurație ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "8867321650").strip()
GEMINI_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
APP_URL = os.getenv("APP_URL") or "https://sesiune-studio.vercel.app"

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "video-generator"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "sesiune_audio.wav")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "sesiune_studio_tiktok.mp4")

# ── Font Loader (Compatibil Windows & Linux) ─────────────────────────────────
def get_font(size, bold=True):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
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

# ── Scenarii Virale de Sesiune cu Structură de Cadre ──────────────────────────
SESIUNE_SCENARIOS = [
    {
        "topic_title": "CUM TRECI DE MATERIA DE BARAJ FĂRĂ RESTANȚĂ",
        "alert_badge": "🎓 SALVARE ÎN SESIUNE",
        "script_speech": "Ești student și te prinde sesiunea nepregătit la cea mai grea materie de baraj? Nu intra în panică și nu toci cursuri de cinci sute de pagini! Secretul celor de zece este principiul optzeci douăzeci: la fiecare examen, doar trei capitole cheie dau peste șaptezeci la sută din subiecte! Pe sesiune-studio.vercel.app ai radarele de catedră decodificate: vezi exact ponderile reale ale profesorilor, spețele rezolvate pe barem și treci sesiunea lejer la buget! Intră acum și salvează-ți sesiunea!",
        "sections": [
            {"time_max": 5.5, "text": "🎓 PANICĂ ÎN SESIUNE?", "color": "#F43F5E"},
            {"time_max": 12.0, "text": "1 • NU TOCI 500 PAGINI", "color": "#F59E0B"},
            {"time_max": 19.5, "text": "2 • PRINCIPIUL 80 / 20", "color": "#6366F1"},
            {"time_max": 26.5, "text": "3 • RADARUL DE CATEDRĂ", "color": "#06B6D4"},
            {"time_max": 99.0, "text": "🔥 TRECI LEJER LA BUGET!", "color": "#10B981"}
        ],
        "tiktok_caption": "📚 Ai materie grea de baraj în sesiune? Nu mai citi haotic 500 de pagini! Află cum decodifici cerințele profesorului și treci examenul direct la buget pe https://sesiune-studio.vercel.app ! 🎓✨ #studenti #sesiune #facultate #sesiunestudio #studentlife #examene #drept #medicina #politehnica #ase"
    },
    {
        "topic_title": "METODA SECRETĂ: CUM ÎNVEȚI PENTRU EXAMEN ÎN DOAR 3 ZILE",
        "alert_badge": "⚡ STRATEGIE DE URGENȚĂ",
        "script_speech": "Ai examen peste trei zile și nici măcar nu ai deschis cursurile? Oprește-te din citit mecanic! Metoda Salvării Rapide funcționează așa: Unu: ia subiectele din anii trecuți și extrage tiparele repetate. Doi: folosește flashcard-uri de memorare activă pentru definiții și formule cheie. Trei: rezolvă probleme direct pe baremul de corectare al profesorului. Toate radarele de curs și spețele rezolvate le găsești pe sesiune-studio.vercel.app! Treci examenul garantat!",
        "sections": [
            {"time_max": 5.0, "text": "⚡ EXAMEN ÎN 3 ZILE?", "color": "#EF4444"},
            {"time_max": 12.0, "text": "1 • TIPARE SUBIECTE VECHI", "color": "#F59E0B"},
            {"time_max": 18.5, "text": "2 • MEMORARE ACTIVĂ", "color": "#8B5CF6"},
            {"time_max": 25.0, "text": "3 • REZOLVARE PE BAREM", "color": "#06B6D4"},
            {"time_max": 99.0, "text": "🎯 EXAMEN PROMOVAT GARANTAT", "color": "#10B981"}
        ],
        "tiktok_caption": "⚡ Cum înveți pentru un examen universitar greu în doar 3 zile fără să pierzi nopțile? Secretul pregătirii pe barem și radare de curs pe https://sesiune-studio.vercel.app ! 🚀📖 #sesiune #student #facultate #invatare #sesiunestudio #examene #bac #studentromania"
    },
    {
        "topic_title": "DE CE PICĂ 60% DINTRE STUDENȚI LA MATERIILE GRELE?",
        "alert_badge": "🛑 CAPCANE DE CATEDRĂ",
        "script_speech": "Știi de ce pică peste șaizeci la sută dintre studenți la materiile grele din facultate? Nu pentru că nu învață, ci pentru că învață greșit! Profesorii caută cuvinte cheie și structura din barem, nu zeci de pagini povestite din memorie! Dacă nu respecți terminologia de catedră, punctajul se înjumătățește instant. Intră pe sesiune-studio.vercel.app, verifică ghidurile de examen pentru facultatea ta și învață inteligent, nu epuizant!",
        "sections": [
            {"time_max": 5.5, "text": "🛑 DE CE PICĂ 60% DIN SERIE?", "color": "#DC2626"},
            {"time_max": 12.5, "text": "NU ÎNVEȚI PREA PUȚIN...", "color": "#F59E0B"},
            {"time_max": 19.5, "text": "CATEDRA VREA CUVINTE CHEIE!", "color": "#6366F1"},
            {"time_max": 25.5, "text": "STRUCTURA BAREMULUI", "color": "#06B6D4"},
            {"time_max": 99.0, "text": "🧠 ÎNVAȚĂ INTELIGENT CU SESIUNESTUDIO", "color": "#10B981"}
        ],
        "tiktok_caption": "🛑 Greșeala fatală pe care o fac 60% dintre studenți în sesiune: tocitul fără barem! Descoperă ce caută profesorii la corectare pe https://sesiune-studio.vercel.app ! 🏛️💡 #sesiune #studenti #facultate #restante #sesiunestudio #examene #viataDeStudent #universitate"
    },
    {
        "topic_title": "CUM ÎȚI PLANIFICI SESIUNEA CA SĂ RĂMÂI LA BUGET",
        "alert_badge": "🏆 BURSE & BUGET",
        "script_speech": "Vrei să iei bursă sau să-ți asiguri locul la buget în anul următor? Iată planul invers de sesiune: împarte zilele de studiu pornind de la cel mai greu examen înapoi, dedică primele ore dimineața capitolelor cu pondere maximă și verifică-te zilnic pe spețe rezolvate. Pe sesiune-studio.vercel.app ai ghidurile complete pe materii, exact ce-ți trebuie ca să iei note mari fără nopți albe!",
        "sections": [
            {"time_max": 5.5, "text": "🏆 BURSE ȘI LOC LA BUGET", "color": "#10B981"},
            {"time_max": 12.5, "text": "PLANIFICAREA INVERSĂ", "color": "#F59E0B"},
            {"time_max": 19.5, "text": "CAPITOLE HIGH-YIELD", "color": "#6366F1"},
            {"time_max": 25.5, "text": "SPEȚE & BAREME REALE", "color": "#06B6D4"},
            {"time_max": 99.0, "text": "🚀 SUCCES ASIGURAT ÎN SESIUNE", "color": "#10B981"}
        ],
        "tiktok_caption": "🏆 Vrei să iei bursă sau să nu treci la taxă? Tehnica planificării inverse în sesiune + radarele de catedră pe https://sesiune-studio.vercel.app ! 🎯✨ #bursa #buget #studenti #sesiune #sesiunestudio #facultate #viataDeStudent #examene"
    }
]

# ── Estimare Proporțională a Timestamp-urilor ─────────────────────────────────
def compute_word_timestamps(text: str, total_duration: float):
    raw_words = text.split()
    if not raw_words:
        return []
    total_chars = sum(len(w) for w in raw_words)
    w_list = []
    curr = 0.05
    for w in raw_words:
        dur = max(0.18, (len(w) / max(1, total_chars)) * total_duration)
        w_list.append({"text": w, "start": curr, "end": curr + dur})
        curr += dur
    return w_list

# ── Generare Audio Feminin Cald & Atrăgător ───────────────────────────────────
async def generate_voice_and_timed_words(script_text: str):
    print("\n[1/3] Generare voce feminină caldă, catifelată și atractivă...")

    # 1. Încercare Gemini TTS Neural cu vocea caldă Aoede
    tts_keys = [
        GEMINI_KEY,
        "",
        ""
    ]
    tts_models = [
        "gemini-2.5-flash-preview-tts",
        "gemini-3.1-flash-tts-preview",
        "gemini-2.5-pro-preview-tts"
    ]
    prompt = f"Citește acest text în limba română cu o voce feminină tânără, foarte caldă, prietenoasă, motivantă și empatică pentru studenți:\n\n{script_text}"

    for key in tts_keys:
        if not key:
            continue
        for model in tts_models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
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
                res = requests.post(url, json=payload, timeout=35)
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
                    print(f"✅ Voce feminină Aoede (caldă & atractivă) generată prin Gemini TTS ({model})! Durată: {duration:.2f}s.")
                    return words, duration, AUDIO_PATH
            except Exception:
                pass

    # 2. Fallback Neural de înaltă fidelitate: Edge-TTS AlinaNeural cu timbru cald & fluid
    print("[Fallback Neural] Generare voce AlinaNeural cu modulație caldă, fluidă și atractivă...")
    import edge_tts
    phonetic_map = {
        "online": "onlain", "site": "sait", "site-ul": "saitul",
        "feedback": "fidbac", "AI": "A I", "BAC": "Bac",
        "sesiune-studio.vercel.app": "Sesiune Studio punct vercel punct app",
        "high-yield": "hai iild", "flashcard": "fleșcard", "flashcard-uri": "fleșcarduri",
        "80/20": "optzeci douăzeci", "60%": "șaizeci la sută", "70%": "șaptezeci la sută", "80%": "optzeci la sută"
    }
    spoken_text = script_text
    for en_word, ro_phonetic in phonetic_map.items():
        spoken_text = spoken_text.replace(en_word, ro_phonetic)

    # Ritm puțin mai relaxat (-2%) și tonalitate catifelată (-1Hz) pentru voce feminină radio-friendly
    communicate = edge_tts.Communicate(
        spoken_text,
        voice="ro-RO-AlinaNeural",
        rate="-2%",
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

    duration = words[-1]["end"] + 0.5 if words else 27.0
    for i in range(min(len(words), len(orig_words))):
        words[i]["text"] = orig_words[i]

    print(f"✅ Voce feminină caldă AlinaNeural generată cu succes! Durată: {duration:.2f}s.")
    return words, duration, AUDIO_PATH

# ── Gruparea Cuvintelor în Fraze Scurte (Subtitrări TikTok) ───────────────────
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

# ── Randare Cadre & Codare Video MP4 cu FFmpeg ────────────────────────────────
def render_video_mp4(scenario, words, total_duration, audio_path):
    print(f"\n[2/3] Randare cadre video 1080x1920 (9:16) la 30 FPS...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    width, height = 1080, 1920
    fps = 30
    total_frames = int(total_duration * fps)

    cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        VIDEO_PATH
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    font_badge = get_font(34, bold=True)
    font_main_title = get_font(54, bold=True)
    font_section = get_font(42, bold=True)
    font_sub_normal = get_font(52, bold=True)
    font_sub_glow = get_font(56, bold=True)
    font_cta = get_font(38, bold=True)
    font_cta_sub = get_font(26, bold=False)

    badge_txt = scenario.get("alert_badge", "🎓 SALVARE ÎN SESIUNE")
    title_txt = scenario.get("topic_title", "CUM TRECI DE MATERIA DE BARAJ")
    sections = scenario.get("sections", [])
    cta_main = "🔥 Treci examenele pe sesiune-studio.vercel.app"
    cta_sub = "Radare de catedră • Spețe pe barem • Flashcards de memorare"

    phrases = build_phrases(words)

    # Pre-generare imagine de fundal cu gradient nobil student (Dark Indigo / Slate)
    bg_base = Image.new("RGB", (width, height), "#0B1120")
    draw_bg = ImageDraw.Draw(bg_base)
    # Gradient radial/linear subtil
    for y in range(height):
        ratio = y / height
        r = int(11 + ratio * 20)
        g = int(17 + ratio * 15)
        b = int(32 + ratio * 45)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))

    # Glow decorativ în fundal (auriu / indigo)
    draw_bg.ellipse([-200, 200, 500, 900], fill=(20, 25, 60))
    draw_bg.ellipse([width - 400, 700, width + 300, 1400], fill=(30, 20, 55))

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = bg_base.copy()
        draw = ImageDraw.Draw(frame)

        # 1. Badge Superior
        b_box = draw.textbbox((0, 0), badge_txt, font=font_badge)
        b_w = (b_box[2] - b_box[0]) + 48
        b_h = 56
        b_x = (width - b_w) // 2
        b_y = 120
        draw.rounded_rectangle([b_x, b_y, b_x + b_w, b_y + b_h], radius=28, fill="#4338CA", outline="#818CF8", width=2)
        draw.text(((width - (b_box[2] - b_box[0])) // 2, b_y + 10), badge_txt, fill="#FFFFFF", font=font_badge)

        # 2. Card Titlu Principal (Efect Sticlă / Glassmorphism)
        card_y, card_w, card_h = 220, 960, 260
        card_x = (width - card_w) // 2
        draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=32, fill="#1E1B4B", outline="#6366F1", width=3)

        # Titlu despicat în două linii
        t_words = title_txt.split()
        mid = len(t_words) // 2
        line1 = " ".join(t_words[:mid])
        line2 = " ".join(t_words[mid:])

        l1_box = draw.textbbox((0, 0), line1, font=font_main_title)
        l2_box = draw.textbbox((0, 0), line2, font=font_main_title)
        draw.text(((width - (l1_box[2] - l1_box[0])) // 2, card_y + 40), line1, fill="#F8FAFC", font=font_main_title)
        draw.text(((width - (l2_box[2] - l2_box[0])) // 2, card_y + 115), line2, fill="#38BDF8", font=font_main_title)

        # 3. Card Dinamic de Secțiune (se schimbă în funcție de timp)
        cur_sec = next((s for s in sections if t <= s["time_max"]), sections[-1] if sections else None)
        if cur_sec:
            sec_txt = cur_sec["text"]
            sec_col = cur_sec["color"]
            s_box = draw.textbbox((0, 0), sec_txt, font=font_section)
            s_w = (s_box[2] - s_box[0]) + 56
            s_h = 76
            s_x = (width - s_w) // 2
            s_y = 530
            draw.rounded_rectangle([s_x, s_y, s_x + s_w, s_y + s_h], radius=24, fill="#111827", outline=sec_col, width=3)
            draw.text(((width - (s_box[2] - s_box[0])) // 2, s_y + 15), sec_txt, fill=sec_col, font=font_section)

        # 4. Zonă Centrală Subtitrări Animate (Karaoke Glow pe Cuvântul Curent)
        cur_phrase = next((p for p in phrases if p["start"] <= t <= p["end"]), None)
        if cur_phrase:
            sub_w = 940
            sub_x = (width - sub_w) // 2
            sub_y = 750
            draw.rounded_rectangle([sub_x, sub_y, sub_x + sub_w, sub_y + 360], radius=32, fill="#0F172A", outline="#334155", width=2)

            # Calcul centrare cuvinte
            total_phrase_w = 0
            space_w = 16
            word_elements = []
            for w in cur_phrase["words"]:
                is_active = w["start"] <= t <= w["end"]
                used_font = font_sub_glow if is_active else font_sub_normal
                bbox = draw.textbbox((0, 0), w["text"], font=used_font)
                w_w = bbox[2] - bbox[0]
                word_elements.append({"word": w, "w": w_w, "active": is_active, "font": used_font})
                total_phrase_w += w_w + space_w

            start_x = (width - total_phrase_w) // 2
            cur_x = max(sub_x + 40, start_x)
            start_y = sub_y + 140

            for elem in word_elements:
                w_obj = elem["word"]
                is_act = elem["active"]
                used_font = elem["font"]
                w_w = elem["w"]

                if is_act:
                    # Glow / Highlight pe cuvântul activ
                    h_box = draw.textbbox((cur_x, start_y), w_obj["text"], font=used_font)
                    draw.rounded_rectangle([h_box[0] - 8, h_box[1] - 4, h_box[2] + 8, h_box[3] + 6], radius=12, fill="#38BDF8")
                    text_fill = "#0F172A"
                else:
                    text_fill = "#F1F5F9"

                draw.text((cur_x, start_y), w_obj["text"], fill=text_fill, font=used_font)
                cur_x += w_w + space_w

        # 5. Card Ilustrativ / Iconițe Valoare
        feat_y = 1220
        feat_w, feat_h = 920, 160
        feat_x = (width - feat_w) // 2
        draw.rounded_rectangle([feat_x, feat_y, feat_x + feat_w, feat_y + feat_h], radius=24, fill="#1E1B4B", outline="#4F46E5", width=2)
        f_title = "⚡ CUM TE AJUTĂ SESIUNESTUDIO?"
        f_sub = "1. Ponderi reale subiecte  •  2. Spețe pe barem  •  3. Flashcards"
        fb_box = draw.textbbox((0, 0), f_title, font=get_font(32, bold=True))
        draw.text(((width - (fb_box[2] - fb_box[0])) // 2, feat_y + 30), f_title, fill="#38BDF8", font=get_font(32, bold=True))
        fsub_box = draw.textbbox((0, 0), f_sub, font=get_font(28, bold=False))
        draw.text(((width - (fsub_box[2] - fsub_box[0])) // 2, feat_y + 90), f_sub, fill="#CBD5E1", font=get_font(28, bold=False))

        # 6. Call to Action Inferior
        cta_y = 1520
        cta_w, cta_h = 940, 120
        cta_x = (width - cta_w) // 2
        draw.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + cta_h], radius=28, fill="#4338CA", outline="#A5B4FC", width=2)
        c_box = draw.textbbox((0, 0), cta_main, font=font_cta)
        draw.text(((width - (c_box[2] - c_box[0])) // 2, cta_y + 22), cta_main, fill="#FFFFFF", font=font_cta)
        cs_box = draw.textbbox((0, 0), cta_sub, font=font_cta_sub)
        draw.text(((width - (cs_box[2] - cs_box[0])) // 2, cta_y + 74), cta_sub, fill="#C7D2FE", font=font_cta_sub)

        # 7. Bară de progres inferioară (Cyan / Indigo gradient)
        prog_w = int((t / total_duration) * width)
        draw.rectangle([0, height - 14, prog_w, height], fill="#38BDF8")

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        print("❌ Eroare FFmpeg la codare video.")
        return False

    mb_size = os.path.getsize(VIDEO_PATH) / (1024 * 1024)
    print(f"✅ Video MP4 randat cu succes: {VIDEO_PATH} ({mb_size:.2f} MB)")
    return True

# ── Trimitere Video MP4 direct pe Telegram (sendVideo) ────────────────────────
def dispatch_video_to_telegram(scenario, duration):
    print("\n[3/3] Trimitere fișier video MP4 și descriere către Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Atenție: Lipsesc credențialele Telegram.")
        return False

    title = scenario.get("topic_title", "Salvare în Sesiune")
    caption_txt = scenario.get("tiktok_caption", "Treci sesiunea pe https://sesiune-studio.vercel.app !")

    tg_caption = (
        f"🎬 <b>[SESIUNESTUDIO - TIKTOK DAILY VIDEO]</b>\n\n"
        f"📌 <b>Subiect:</b> {title}\n"
        f"⏱ <b>Durată:</b> {duration:.0f} secunde | Format 9:16 (1080x1920)\n\n"
        f"📋 <b>Descrierea de copiat pe TikTok</b> <i>(atinge textul pentru copiere automată):</i>\n\n"
        f"<code>{caption_txt}</code>\n\n"
        f"👉 <i>Descarcă videoclipul MP4 atașat și postează-l direct pe TikTok / Instagram Reels / YouTube Shorts!</i>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(VIDEO_PATH, "rb") as vf:
        files = {"video": ("sesiune_studio_tiktok.mp4", vf, "video/mp4")}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": tg_caption,
            "parse_mode": "HTML",
            "supports_streaming": True
        }
        res = requests.post(url, data=data, files=files, timeout=120)

    res_json = res.json()
    if res_json.get("ok"):
        print("✅ Fișierul video MP4 SESIUNESTUDIO a fost expediat cu succes pe Telegram!")
        return True
    else:
        print(f"❌ Eroare Telegram: {res_json.get('description')}")
        return False

# ── Entrypoint Asincron ───────────────────────────────────────────────────────
async def main():
    day_idx = datetime.now().timetuple().tm_yday % len(SESIUNE_SCENARIOS)
    scenario = SESIUNE_SCENARIOS[day_idx]
    print(f"🎬 Scenariu selectat: {scenario['topic_title']}")

    words, duration, audio_path = await generate_voice_and_timed_words(scenario["script_speech"])
    success = render_video_mp4(scenario, words, duration, audio_path)
    if success:
        dispatch_video_to_telegram(scenario, duration)

if __name__ == "__main__":
    asyncio.run(main())
