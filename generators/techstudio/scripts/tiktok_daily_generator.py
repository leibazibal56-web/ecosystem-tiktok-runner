# -*- coding: utf-8 -*-
"""
TechStudio IT - TikTok, Reels & Shorts Daily Video Generator
- Generates 9:16 vertical videos (1080x1920) with Gemini 2.5 Flash TTS warm female voice (Aoede) / Edge-TTS (AlinaNeural).
- Uses Gemini 2.5 Flash to synthesize fresh educational scenarios with 4 curated fallbacks.
- Dispatches final MP4 video and copy-paste caption directly to the admin Telegram bot.
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

GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "8867321650").strip()
APP_URL = (os.getenv("APP_URL") or "https://techstudio-ro.vercel.app").strip()

OUTPUT_DIR = os.path.abspath(os.path.join(ROOT_DIR, "video-generator"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "daily_audio.wav")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "techstudio_tiktok.mp4")

FALLBACK_TOPICS = [
    {
        "topic_title": "3 ÎNTREBĂRI DE SYSTEM DESIGN CARE DECID SALARIUL LA INTERVIUL IT",
        "alert_badge": "INTERVIU TEHNIC IT",
        "script_speech": "Mergi la un interviu tehnic pentru un rol de Mid sau Senior Developer în România? Iată trei întrebări de arhitectură și baze de date care fac diferența la ofertă! Unu: De ce nu ajută un index B-Tree în S Q L atunci când cauți cu wildcard la începutul șirului? Pentru că motorul face Full Table Scan! Doi: Cum previi fenomenul de Cache Stampede în Redis când expiră o cheie populară? Folosești blocare distribuită sau recalculare asincronă! Trei: Diferența dintre idempotență la P U T și P O S T în microservicii! Exersează pe techstudio-ro.vercel.app!",
        "sections": [
            {
                "time_max": 6.5,
                "text": "3 ÎNTREBĂRI CHEIE INTERVIU IT",
                "color": "#06B6D4"
            },
            {
                "time_max": 14.0,
                "text": "1 • SQL INDEX & FULL TABLE SCAN",
                "color": "#2563EB"
            },
            {
                "time_max": 21.5,
                "text": "2 • PREVENIRE CACHE STAMPEDE REDIS",
                "color": "#F59E0B"
            },
            {
                "time_max": 27.5,
                "text": "3 • IDEMPOTENȚA ÎN MICROSERVICII",
                "color": "#10B981"
            },
            {
                "time_max": 99.0,
                "text": "SOLUȚIE • SIMULATOR TECHSTUDIO",
                "color": "#10B981"
            }
        ],
        "tiktok_caption": "Te pregătești pentru un interviu tehnic în IT? 3 întrebări clasice de SQL, Caching și System Design explicate pe https://techstudio-ro.vercel.app ! 💻🚀 #itromania #programare #systemdesign #devops"
    }
]

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

def generate_scenario_with_gemini():
    import datetime
    day_idx = datetime.datetime.now().timetuple().tm_yday % len(FALLBACK_TOPICS)
    print(f"[1/4] Solicitare scenariu nou prin Gemini 2.5 Flash pentru TechStudio IT...")
    if not GEMINI_API_KEY:
        return FALLBACK_TOPICS[day_idx]

    prompt = (
        f"Ești scenaristul oficial pentru conținutul video scurt (TikTok / Reels) al platformei TechStudio IT (https://techstudio-ro.vercel.app) - specializată în pregătirea interviurilor tehnice în IT în România (Software Engineering, System Design, Structuri de Date și Algoritmi, SQL indexing, DevOps & Cloud Architecture).\n"
        "Folosește EXCLUSIV limba română literară corectă conform DOOM3, cu diacritice complete.\n"
        "Creează un scenariu alert de 25-30 secunde (65-75 cuvinte) cu Hook în primele 4 secunde, 3 puncte clare și îndemn final de accesare a platformei.\n"
        "RĂSPUNDE EXCLUSIV ÎN FORMAT JSON VALID:\n"
        "{\n"
        '  "topic_title": "TITLU CU MAJUSCULE (max 6 cuvinte)",\n'
        '  "alert_badge": "CATEGORIE (max 3 cuvinte)",\n'
        '  "script_speech": "Textul rostit în limba română (65-75 cuvinte).",\n'
        '  "sections": [\n'
        '    {"time_max": 6.5, "text": "TITLU HOOK", "color": "#DC2626"},\n'
        '    {"time_max": 14.0, "text": "1 • PUNCTUL UNU", "color": "#2563EB"},\n'
        '    {"time_max": 21.5, "text": "2 • PUNCTUL DOI", "color": "#F59E0B"},\n'
        '    {"time_max": 27.5, "text": "3 • PUNCTUL TREI", "color": "#06B6D4"},\n'
        '    {"time_max": 99.0, "text": "SOLUȚIE • VERIFICĂ ACUM", "color": "#10B981"}\n'
        '  ],\n'
        '  "tiktok_caption": "Descriere captivantă cu linkul https://techstudio-ro.vercel.app și hashtag-uri: #programare #interviuit #softwareengineer #systemdesign #itromania #techstudio"\n'
        "}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.75, "response_mime_type": "application/json"}}
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            parsed = json.loads(raw_text)
            if all(k in parsed for k in ("topic_title", "script_speech", "sections", "tiktok_caption")):
                print(f"✅ Scenariu generat cu succes: {parsed.get('topic_title')}")
                return parsed
    except Exception as e:
        print(f"Atenție apel Gemini ({e}). Se folosește scenariul local verificat.")
    return FALLBACK_TOPICS[day_idx]

def compute_word_timestamps(script_text, total_duration):
    words = script_text.split()
    weights = []
    for w in words:
        clean = w.rstrip(".,?!:;")
        base = max(1, len(clean))
        pause = 3.5 if any(w.endswith(p) for p in [".", "?", "!"]) else (2.0 if any(w.endswith(p) for p in [",", ":", ";"]) else 0.0)
        weights.append(base + pause)
    total_w = sum(weights) or 1.0
    scale = (total_duration - 0.4) / total_w
    cur_t = 0.25
    timed = []
    for i, w in enumerate(words):
        dur = weights[i] * scale
        clean_len = max(1, len(w.rstrip(".,?!:;")))
        speak_dur = max(0.18, (clean_len / weights[i]) * dur)
        timed.append({"text": w, "start": cur_t, "end": cur_t + speak_dur})
        cur_t += dur
    return timed

async def generate_audio_and_timestamps(script_text):
    print("[2/4] Generare voce neurală feminină în limba română...")
    import base64
    import wave
    tts_models = ["gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"]
    prompt = f"Citește cu o voce feminină caldă, clară, naturală și sigură în limba română următorul text educațional:\n\n{script_text}"
    if GEMINI_API_KEY:
        for model in tts_models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Aoede"}}}
                    }
                }
                res = requests.post(url, json=payload, timeout=45)
                if res.status_code == 200:
                    b64 = res.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
                    pcm = base64.b64decode(b64)
                    with wave.open(AUDIO_PATH, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(24000)
                        wf.writeframes(pcm)
                    duration = len(pcm) / 48000.0
                    words = compute_word_timestamps(script_text, duration)
                    print(f"✅ Voce Aoede generată ({duration:.2f}s, {len(words)} cuvinte).")
                    return words, duration, AUDIO_PATH
            except Exception as e:
                print(f"Notice TTS {model}: {e}")

    import edge_tts
    communicate = edge_tts.Communicate(script_text, voice="ro-RO-AlinaNeural", rate="-2%", pitch="+2Hz", boundary="WordBoundary")
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
    if not words:
        words = compute_word_timestamps(script_text, duration)
    else:
        for i in range(min(len(words), len(orig_words))):
            words[i]["text"] = orig_words[i]
    print(f"✅ Voce AlinaNeural generată ({duration:.2f}s, {len(words)} cuvinte).")
    return words, duration, AUDIO_PATH

def build_phrases(words):
    phrases = []
    current = []
    for w in words:
        current.append(w)
        has_punct = any(w["text"].endswith(p) for p in [".", "?", "!", ":", ";"])
        if len(current) >= 4 or (len(current) >= 2 and has_punct):
            phrases.append({"words": current, "start": current[0]["start"], "end": current[-1]["end"] + 0.15})
            current = []
    if current:
        phrases.append({"words": current, "start": current[0]["start"], "end": current[-1]["end"] + 0.2})
    return phrases

def render_video(scenario, words, total_duration, audio_path):
    print("[3/4] Randare video 1080x1920 @ 30fps cu FFmpeg libx264...")
    width, height = 1080, 1920
    fps = 30
    total_frames = max(1, int(total_duration * fps))
    phrases = build_phrases(words)
    sections = scenario.get("sections", [])

    base_bg = Image.new("RGB", (width, height), "#0B0F19")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(height):
        ratio = y / height
        r = int(8 * (1 - ratio) + 15 * ratio)
        g = int(14 * (1 - ratio) + 23 * ratio)
        b = int(32 * (1 - ratio) + 42 * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))
    draw_bg.rounded_rectangle([60, 680, width - 60, 1260], radius=40, fill="#0F172A", outline="#1E293B", width=2)

    font_brand = get_font(34, bold=True)
    font_section = get_font(38, bold=True)
    font_word = get_font(60, bold=True)
    font_word_sm = get_font(40, bold=True)
    font_cta = get_font(32, bold=True)
    font_cta_sub = get_font(26, bold=True)
    font_disclaimer = get_font(22, bold=False)

    def get_w_font(t_str):
        return font_word_sm if len(t_str) > 16 else font_word

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24", "-r", str(fps), "-i", "-", "-i", audio_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "faster", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", "-shortest", VIDEO_PATH
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    brand_text = "💻 TECHSTUDIO • INTERVIURI TEHNICE IT & ARHITECTURĂ"
    cta_main = "Antrenează-te pentru interviul IT pe techstudio-ro.vercel.app"
    cta_sub = "Algoritmi, System Design, Cloud, DevOps & Securitate Cibernetică"
    disc1 = "Platformă de pregătire pentru interviurile tehnice din industria IT & Software Engineering."
    disc2 = "Structuri de date, arhitectură distribuită, baze de date SQL/NoSQL și studii de caz."

    def get_current_section(t):
        for sec in sections:
            if t <= sec.get("time_max", 999):
                return sec.get("text", "TechStudio IT"), sec.get("color", "#06B6D4")
        return "SOLUȚIE • ACCESEAZĂ PLATFORMA", "#10B981"

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)

        pill_w, pill_h = 820, 68
        pill_x = (width - pill_w) // 2
        pill_y = 200
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=34, fill="#1E293B", outline="#06B6D4", width=2)
        b_box = draw.textbbox((0, 0), brand_text, font=font_brand)
        draw.text(((width - (b_box[2] - b_box[0])) // 2, pill_y + 15), brand_text, fill="#38BDF8", font=font_brand)

        sec_text, sec_color = get_current_section(t)
        sec_bbox = draw.textbbox((0, 0), sec_text, font=font_section)
        sec_w = sec_bbox[2] - sec_bbox[0]
        s_pad = 28
        draw.rounded_rectangle([(width - sec_w)//2 - s_pad, 315, (width + sec_w)//2 + s_pad, 385], radius=16, fill=sec_color)
        draw.text(((width - sec_w) // 2, 325), sec_text, fill="#FFFFFF", font=font_section)

        active_phrase = next((p for p in phrases if p["start"] <= t <= p["end"]), None)
        if not active_phrase:
            active_phrase = next((p for p in phrases if p["start"] > t), phrases[-1] if phrases else None)

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
                    if w["start"] <= t <= w["end"] + 0.05:
                        draw.rounded_rectangle([cur_x - 16, cur_y - 10, cur_x + ww + 16, cur_y + wh + 10], radius=12, fill="#FACC15")
                        draw.text((cur_x, cur_y), w["text"].upper(), fill="#000000", font=f_cur)
                    else:
                        draw.text((cur_x + 2, cur_y + 2), w["text"].upper(), fill="#000000", font=f_cur)
                        draw.text((cur_x, cur_y), w["text"].upper(), fill="#FFFFFF", font=f_cur)
                    cur_x += ww + spacing
            else:
                half = max(1, len(p_words) // 2)
                lines = [p_words[:half], p_words[half:]]
                cur_y = 860
                for line in lines:
                    if not line:
                        continue
                    line_boxes = [draw.textbbox((0, 0), w["text"].upper(), font=get_w_font(w["text"])) for w in line]
                    line_w = sum(b[2] - b[0] for b in line_boxes) + spacing * (len(line) - 1)
                    cur_x = (width - line_w) // 2
                    for i, w in enumerate(line):
                        f_cur = get_w_font(w["text"])
                        ww = line_boxes[i][2] - line_boxes[i][0]
                        wh = line_boxes[i][3] - line_boxes[i][1]
                        if w["start"] <= t <= w["end"] + 0.05:
                            draw.rounded_rectangle([cur_x - 16, cur_y - 10, cur_x + ww + 16, cur_y + wh + 10], radius=12, fill="#FACC15")
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#000000", font=f_cur)
                        else:
                            draw.text((cur_x + 2, cur_y + 2), w["text"].upper(), fill="#000000", font=f_cur)
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#FFFFFF", font=f_cur)
                        cur_x += ww + spacing
                    cur_y += 120

        progress = min(1.0, t / total_duration)
        bar_left, bar_right = 80, width - 80
        bar_y = 1560
        draw.rounded_rectangle([bar_left, bar_y, bar_right, bar_y + 12], radius=6, fill="#1E293B")
        fill_w = int(bar_left + (bar_right - bar_left) * progress)
        if fill_w > bar_left + 6:
            draw.rounded_rectangle([bar_left, bar_y, fill_w, bar_y + 12], radius=6, fill="#06B6D4")

        c1_box = draw.textbbox((0, 0), cta_main, font=font_cta)
        c2_box = draw.textbbox((0, 0), cta_sub, font=font_cta_sub)
        draw.text(((width - (c1_box[2] - c1_box[0])) // 2, 1620), cta_main, fill="#38BDF8", font=font_cta)
        draw.text(((width - (c2_box[2] - c2_box[0])) // 2, 1680), cta_sub, fill="#94A3B8", font=font_cta_sub)

        d1_box = draw.textbbox((0, 0), disc1, font=font_disclaimer)
        d2_box = draw.textbbox((0, 0), disc2, font=font_disclaimer)
        draw.text(((width - (d1_box[2] - d1_box[0])) // 2, 1770), disc1, fill="#64748B", font=font_disclaimer)
        draw.text(((width - (d2_box[2] - d2_box[0])) // 2, 1805), disc2, fill="#64748B", font=font_disclaimer)

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    stderr_text = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    proc.wait()
    if proc.returncode != 0:
        print("Eroare FFmpeg:", stderr_text)
        return False
    print(f"✅ Video randat cu succes: {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH)/(1024*1024):.2f} MB)")
    return True

def dispatch_to_telegram(scenario, duration):
    print("[4/4] Trimitere videoclip pe Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Lipsesc credențialele Telegram.")
        return False
    title = scenario.get("topic_title", "TechStudio IT TikTok")
    caption_txt = scenario.get("tiktok_caption", "Accesează https://techstudio-ro.vercel.app !")
    tg_caption = (
        f"🎬 <b>[TECHSTUDIO IT TIKTOK DAILY]</b>\n\n"
        f"📌 <b>Subiect:</b> {title}\n"
        f"⏱ <b>Durată:</b> {duration:.0f}s | Format 9:16 (1080x1920)\n\n"
        f"📋 <b>Atinge textul din caseta de mai jos</b> <i>(se copiază automat în clipboard):</i>\n\n"
        f"<code>{caption_txt}</code>\n\n"
        f"📲 <i>Apasă pe video → Salvează / Descarcă → Lipește descrierea direct în TikTok / Reels!</i>"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(VIDEO_PATH, "rb") as vf:
        files = {"video": ("techstudio_tiktok.mp4", vf, "video/mp4")}
        data = {"chat_id": TELEGRAM_CHAT_ID, "caption": tg_caption, "parse_mode": "HTML", "supports_streaming": True}
        res = requests.post(url, data=data, files=files, timeout=120)
    res_json = res.json()
    if res_json.get("ok"):
        print("✅ Videoclipul TechStudio IT a fost expediat cu succes pe Telegram!")
        return True
    print(f"❌ Eroare Telegram: {res_json}")
    return False

async def main():
    scenario = generate_scenario_with_gemini()
    words, duration, audio_path = await generate_audio_and_timestamps(scenario["script_speech"])
    if render_video(scenario, words, duration, audio_path):
        dispatch_to_telegram(scenario, duration)

if __name__ == "__main__":
    asyncio.run(main())
