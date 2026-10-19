# -*- coding: utf-8 -*-
"""
GovTalent România - TikTok & Reels Daily Automated Video Generator
- Generates 9:16 vertical video (1080x1920) with Romanian Neural TTS (edge-tts) and word-by-word dynamic subtitles.
- Uses Gemini 2.0 Flash to synthesize fresh, high-converting educational scenarios about Romanian public sector hiring,
  ANFP National Exam (SENEOSP), psychometric testing, and administrative law traps.
- Dispatches final MP4 video and copy-paste caption directly to the admin Telegram bot for 1-click posting on TikTok.
- Designed to run seamlessly both locally on Windows and in GitHub Actions (Ubuntu).
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "daily_audio.mp3")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "daily_tiktok.mp4")

# ── Fallback Topics Tailored to GovTalent Romania ─────────────────
FALLBACK_TOPICS = [
    {
        "topic_title": "3 GREȘELI CARE TE PICĂ LA CONCURSUL NAȚIONAL ANFP",
        "alert_badge": "CONCURSUL NAȚIONAL 2026",
        "script_speech": "Vrei să intri în sistemul public sau să devii funcționar public? Iată trei greșeli majore care elimină peste jumătate dintre candidați! Unu: Barem strict de cincizeci la sută la fiecare secțiune din proba preliminară SENEOSP. Dacă iei nouăzeci la sută la drept, dar pici la limba străină sau IT, ești respins direct! Doi: Ignorarea itemilor inversați de la testul psihometric. Dacă nu ești consecvent, algoritmul te depistează ca distorsiune deliberată. Trei: Calculul greșit al vechimii în specialitate. Verifică-ți gratuit eligibilitatea și testează grilele pe govtalent-romania.vercel.app!",
        "sections": [
            {"time_max": 6.0, "text": "CONCURSUL NAȚIONAL ANFP", "color": "#002B7F"},
            {"time_max": 13.5, "text": "1 • BAREMUL ELIMINATORIU 50%", "color": "#DC2626"},
            {"time_max": 20.5, "text": "2 • TESTAREA PSIHOMETRICĂ", "color": "#D97706"},
            {"time_max": 27.5, "text": "3 • CALCUL VECHIME ÎN SPECIALITATE", "color": "#2563EB"},
            {"time_max": 99.0, "text": "TESTEAZĂ GRATUIT PE GOVTALENT", "color": "#059669"}
        ],
        "tiktok_caption": "Atenție dacă vrei să lucrezi la stat în 2026! 🏛️ 3 greșeli majore care te pică la Concursul Național ANFP și cum să le eviți. Testează-ți gratuit eligibilitatea și grilele oficiale pe govtalent-romania.vercel.app! 🇷🇴 #concursnational #anfp #functionarpublic #stat #angajarestabilitate #govtalent #romania"
    },
    {
        "topic_title": "CUM SE CALCULEAZĂ VECHIMEA ÎN SPECIALITATE LA STAT",
        "alert_badge": "VECHIME ART. 475",
        "script_speech": "Știai că vechimea în muncă nu este același lucru cu vechimea în specialitate pentru concursurile de stat? Conform articolului 475 din Codul administrativ, vechimea în specialitate curge strict din ziua absolvirii facultății cu diplomă de licență și doar dacă atribuțiile din fișa postului corespund funcției publice vizate. Dacă ai lucrat cinci ani în privat ca vânzător și ai diplomă în administrație publică, vechimea ta în specialitate este zero! Folosește calculatorul legal gratuit pe govtalent-romania.vercel.app!",
        "sections": [
            {"time_max": 6.0, "text": "CALCUL VECHIME LA STAT", "color": "#002B7F"},
            {"time_max": 13.5, "text": "ATENȚIE: VECHIMEA ÎN MUNCĂ NU AJUNGE", "color": "#DC2626"},
            {"time_max": 21.0, "text": "REGULA: DUPĂ DIPLOMA DE LICENȚĂ", "color": "#D97706"},
            {"time_max": 27.5, "text": "CORESPONDENȚĂ ATRIBUȚII FIȘĂ POST", "color": "#2563EB"},
            {"time_max": 99.0, "text": "CALCULATOR GRATUIT GOVTALENT", "color": "#059669"}
        ],
        "tiktok_caption": "Nu-ți depune dosarul la stat înainte să verifici asta! ⚠️ Cum se calculează legal vechimea în specialitate conform art. 475 Codul Administrativ. Calculează gratuit pe govtalent-romania.vercel.app! 💼 #vechime #functionarpublic #stat #angajare #dosarconcurs #govtalent #romania"
    },
    {
        "topic_title": "BAREMUL SECRET LA TESTUL PSIHOMETRIC ANFP",
        "alert_badge": "TEST PSIHOMETRIC",
        "script_speech": "De ce pică peste 60% dintre candidați la Testarea Avansată Psihometrică de la stat? Iată secretul baremului oficial! Unu: Ai o scală de la 1 la 10, dar rezultatele se convertesc în note de la 1 la 5. Pragul minim este nota 3 la fiecare competență! Doi: Dacă pici o singură competență din cele opt, ești respins pe loc, chiar dacă la celelalte ai nota 5. Trei: Chestionarul conține aserțiuni inversate pentru controlul minciunii. Antrenează-te pe simulatorul real cu raport complet pe govtalent-romania.vercel.app!",
        "sections": [
            {"time_max": 6.0, "text": "SECRETUL PSIHOMETRIC ANFP", "color": "#002B7F"},
            {"time_max": 13.0, "text": "1 • SCALARE FORMULĂ NOTE 1-5", "color": "#2563EB"},
            {"time_max": 20.5, "text": "2 • NOTA MINIMĂ 3.00 OBLIGATORIE", "color": "#DC2626"},
            {"time_max": 27.0, "text": "3 • ITEMI INVERSAȚI DE MINCIUNĂ", "color": "#D97706"},
            {"time_max": 99.0, "text": "ANTRENEAZĂ-TE PE GOVTALENT", "color": "#059669"}
        ],
        "tiktok_caption": "Secretul de la Testul Psihometric ANFP pe care nimeni nu ți-l spune! 🧠 Nota minimă 3.00 este eliminatorie la fiecare competență. Simulează chestionarul complet pe govtalent-romania.vercel.app! 🇷🇴 #psihometric #anfp #concursstat #functionarpublic #govtalent #romania"
    },
    {
        "topic_title": "TOP 5 POSTURI LA STAT CU SPOR DE 50% SALARIU",
        "alert_badge": "SPORURI SALARIALE 2026",
        "script_speech": "Vrei un salariu de top în administrația publică? Iată posturile cu cele mai mari sporuri legale! Unu: Experți în achiziții publice SEAP și SICAP. Beneficiază de sporuri de complexitate și cerere uriașă în primării. Doi: Manageri de proiecte pe fonduri europene și PNRR, cu spor salarial legal de până la 50%! Trei: Auditori publici interni atestați UCAAPI și responsabili de control financiar preventiv. Învață legislația tehnică și pregătește-ți dosarul pe govtalent-romania.vercel.app!",
        "sections": [
            {"time_max": 6.0, "text": "POSTURI CU SPORURI LA STAT", "color": "#002B7F"},
            {"time_max": 13.0, "text": "1 • ACHIZIȚII PUBLICE SICAP", "color": "#2563EB"},
            {"time_max": 21.0, "text": "2 • PROIECTE EUROPENE PNRR (+50%)", "color": "#059669"},
            {"time_max": 27.5, "text": "3 • AUDIT PUBLIC UCAAPI & CFPP", "color": "#D97706"},
            {"time_max": 99.0, "text": "MODULE SPECIALIZATE GOVTALENT", "color": "#002B7F"}
        ],
        "tiktok_caption": "Posturile de la stat care îți aduc sporuri salariale de până la 50%! 📈 Achiziții SICAP, Proiecte Europene PNRR și Audit Public Intern. Află cerințele de dosar pe govtalent-romania.vercel.app! 💶 #salariustat #pnrr #achizitiipublice #audit #govtalent #romania"
    },
    {
        "topic_title": "CAPCANA LA INTERVIUL DE CONCURS LA STAT",
        "alert_badge": "INTERVIU METODA STAR",
        "script_speech": "Ce răspunzi la interviul de concurs dacă președintele comisiei te întreabă: Ce faci dacă șeful ierarhic îți cere verbal să avizezi un dosar nelegal? Mulți răspund că respectă ierarhia și sunt picați instant! Conform articolului 437 din Codul administrativ, ești obligat prin lege să refuzi în scris și motivat îndeplinirea ordinului vădit nelegal! Antrenează-te pe simulatorul audio de interviu pe metoda STAR pe govtalent-romania.vercel.app!",
        "sections": [
            {"time_max": 6.0, "text": "CAPCANĂ LA INTERVIU ANFP", "color": "#DC2626"},
            {"time_max": 14.0, "text": "ÎNTREBARE: DISPOZIȚIE IERARHICĂ ILEGALĂ", "color": "#002B7F"},
            {"time_max": 21.5, "text": "RĂSPUNS GREȘIT: RESPECT IERARHIA (PICAT)", "color": "#DC2626"},
            {"time_max": 28.0, "text": "RĂSPUNS CORECT: REFUZ ÎN SCRIS (ART. 437)", "color": "#059669"},
            {"time_max": 99.0, "text": "SIMULATOR AUDIO PE GOVTALENT", "color": "#2563EB"}
        ],
        "tiktok_caption": "Întrebarea capcană la interviul pentru un post la stat! 🏛️ Cum să răspunzi conform art. 437 Codul Administrativ fără să fii eliminat. Antrenează-te cu simulatorul vocal pe govtalent-romania.vercel.app! ⚖️ #interviu #functionarpublic #stat #concursuri #star #govtalent #romania"
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

# ── 1. Gemini Content Generation ──────────────────────────────────
def generate_scenario_with_gemini():
    print("[1/4] Solicitare scenariu nou de TikTok prin Gemini 2.0 Flash...")
    if not GEMINI_API_KEY:
        print("Avertisment: GEMINI_API_KEY lipsește. Se folosește scenariu din baza locală.")
        return random.choice(FALLBACK_TOPICS)

    prompt = (
        "Ești scenaristul oficial de marketing educațional pentru conținut video scurt (TikTok / Reels) al platformei GovTalent România (govtalent-romania.vercel.app).\n"
        "GovTalent este sistemul #1 de pregătire și orientare pentru Concursul Național ANFP și posturile din sectorul public din România (calculator vechime art. 475, simulator SENEOSP, test psihometric, interviu STAR, achiziții SICAP, fonduri PNRR).\n"
        "Creează un scenariu captivant, alert, de 25-30 de secunde (aproximativ 65-75 de cuvinte), pe o temă de mare interes pentru românii care vor un post stabil la stat.\n"
        "Exemple de teme: calculul legal al vechimii în specialitate, baremul de 50% la SENEOSP, capcanele de la testarea psihologică ANFP, diferența funcționar public vs contractual, sporuri salariale PNRR de 50%, întrebări grele la interviul de concurs.\n\n"
        "RĂSPUNDE EXCLUSIV ÎN FORMAT JSON VALID conform acestei scheme fără alte comentarii:\n"
        "{\n"
        '  "topic_title": "TITLU CU MAJUSCULE (max 6 cuvinte)",\n'
        '  "alert_badge": "CATEGORIE (max 3 cuvinte)",\n'
        '  "script_speech": "Textul rostit în limba română (65-75 cuvinte). Trebuie să aibă Hook în primele 4 secunde, 3 puncte numerotate Unu/Doi/Trei și un îndemn final de testare gratuită pe govtalent-romania.vercel.app.",\n'
        '  "sections": [\n'
        '    {"time_max": 6.0, "text": "TITLU SECȚIUNE HOOK", "color": "#002B7F"},\n'
        '    {"time_max": 13.5, "text": "1 • PUNCT UNU", "color": "#DC2626"},\n'
        '    {"time_max": 20.5, "text": "2 • PUNCT DOI", "color": "#D97706"},\n'
        '    {"time_max": 27.5, "text": "3 • PUNCT TREI", "color": "#2563EB"},\n'
        '    {"time_max": 99.0, "text": "TESTEAZĂ GRATUIT PE GOVTALENT", "color": "#059669"}\n'
        '  ],\n'
        '  "tiktok_caption": "Descriere captivantă pentru TikTok cu 4-6 hashtag-uri relevante în română (#anfp #concursnational #functionarpublic #stat #govtalent #romania)."\n'
        "}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "topP": 0.95}
    }
    try:
        res = requests.post(url, json=payload, timeout=20)
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
            return random.choice(FALLBACK_TOPICS)
    except Exception as e:
        print(f"Atenție la apelul Gemini: {e}. Se trece pe fallback.")
        return random.choice(FALLBACK_TOPICS)

# ── 2. Romanian Neural Audio & Timestamps ─────────────────────────
async def generate_audio_and_timestamps(script_text):
    print("[2/4] Generare audio neuronal românesc și timestamp-uri pe cuvinte...")
    voices = ["ro-RO-EmilNeural", "ro-RO-AlinaNeural"]
    selected_voice = random.choice(voices)
    
    communicate = edge_tts.Communicate(
        script_text,
        voice=selected_voice,
        rate="+12%",
        boundary="WordBoundary"
    )
    
    words = []
    audio_data = bytearray()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            w_text = chunk["text"].strip()
            if not w_text:
                continue
            start_s = chunk["offset"] / 10_000_000.0
            dur_s = chunk["duration"] / 10_000_000.0
            words.append({
                "text": w_text,
                "start": start_s,
                "end": start_s + dur_s
            })
            
    with open(AUDIO_PATH, "wb") as f:
        f.write(audio_data)
        
    duration = words[-1]["end"] + 0.5 if words else 30.0
    print(f"Audio salvat: {len(audio_data)} bytes, {len(words)} cuvinte, voce: {selected_voice}, durată: {duration:.2f}s")
    return words, duration

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

def render_video(scenario, words, total_duration):
    print("[3/4] Randare cadre video 1080x1920 și codare FFmpeg x264...")
    width, height = 1080, 1920
    fps = 30
    total_frames = int(total_duration * fps)
    phrases = build_phrases(words)
    sections = scenario.get("sections", [])
    
    # Base background gradient (Deep blue / Slate official)
    base_bg = Image.new("RGB", (width, height), "#0B0F19")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(height):
        ratio = y / height
        r = int(10 * (1 - ratio) + 5 * ratio)
        g = int(22 * (1 - ratio) + 10 * ratio)
        b = int(48 * (1 - ratio) + 20 * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))
        
    # National Tricolor top bar
    draw_bg.rectangle([0, 0, width // 3, 14], fill="#002B7F")
    draw_bg.rectangle([width // 3, 0, 2 * (width // 3), 14], fill="#FCD116")
    draw_bg.rectangle([2 * (width // 3), 0, width, 14], fill="#CE1126")

    # Ambient rounded card in center for dynamic subtitles
    draw_bg.rounded_rectangle([60, 680, width - 60, 1260], radius=40, fill="#111827", outline="#1E293B", width=2)
    
    # Load fonts
    font_brand = get_font(34, bold=True)
    font_section = get_font(38, bold=True)
    font_word = get_font(60, bold=True)
    font_cta = get_font(36, bold=True)
    font_cta_sub = get_font(28, bold=True)
    font_disclaimer = get_font(20, bold=False)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", AUDIO_PATH,
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
    brand_text = "GOVTALENT ROMÂNIA  •  CONCURSURI DE STAT"
    cta_main = "Testează gratuit pe govtalent-romania.vercel.app"
    cta_sub = "Calculator vechime legală • Grile ANFP • Test psihometric"
    disc1 = "Platformă educațională independentă. Operator: TEODORESCU O. DIANA PFA (CAEN 8559)."
    disc2 = "Conținut orientativ conform OUG 57/2019 și OUG 121/2023. Fără garanția promovării."
    
    def get_current_section(t):
        for sec in sections:
            if t <= sec.get("time_max", 999):
                return sec.get("text", "CONCURSUL NAȚIONAL 2026"), sec.get("color", "#002B7F")
        return "TESTEAZĂ GRATUIT PE GOVTALENT", "#059669"
        
    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)
        
        # 1. Top Brand Pill
        pill_w, pill_h = 760, 68
        pill_x = (width - pill_w) // 2
        pill_y = 200
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=34, fill="#1E293B", outline="#FCD116", width=2)
        b_box = draw.textbbox((0, 0), brand_text, font=font_brand)
        draw.text(((width - (b_box[2] - b_box[0])) // 2, pill_y + 15), brand_text, fill="#FCD116", font=font_brand)
        
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
                        draw.rounded_rectangle([cur_x - 16, cur_y - 10, cur_x + ww + 16, cur_y + wh + 10], radius=12, fill="#FCD116")
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
                            draw.rounded_rectangle([cur_x - 16, cur_y - 10, cur_x + ww + 16, cur_y + wh + 10], radius=12, fill="#FCD116")
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#000000", font=font_word)
                        else:
                            draw.text((cur_x + 2, cur_y + 2), w["text"].upper(), fill="#000000", font=font_word)
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#FFFFFF", font=font_word)
                        cur_x += ww + spacing
                    cur_y += 120

        # 4. Progress Bar
        progress = min(1.0, t / total_duration)
        bar_left, bar_right = 80, width - 80
        bar_y = 1560
        draw.rounded_rectangle([bar_left, bar_y, bar_right, bar_y + 12], radius=6, fill="#1E293B")
        fill_w = int(bar_left + (bar_right - bar_left) * progress)
        if fill_w > bar_left + 6:
            draw.rounded_rectangle([bar_left, bar_y, fill_w, bar_y + 12], radius=6, fill="#FCD116")
            
        # 5. Call To Action
        c1_box = draw.textbbox((0, 0), cta_main, font=font_cta)
        c2_box = draw.textbbox((0, 0), cta_sub, font=font_cta_sub)
        draw.text(((width - (c1_box[2] - c1_box[0])) // 2, 1620), cta_main, fill="#38BDF8", font=font_cta)
        draw.text(((width - (c2_box[2] - c2_box[0])) // 2, 1680), cta_sub, fill="#94A3B8", font=font_cta_sub)
        
        # 6. Legal Micro Disclaimer
        d1_box = draw.textbbox((0, 0), disc1, font=font_disclaimer)
        d2_box = draw.textbbox((0, 0), disc2, font=font_disclaimer)
        draw.text(((width - (d1_box[2] - d1_box[0])) // 2, 1770), disc1, fill="#64748B", font=font_disclaimer)
        draw.text(((width - (d2_box[2] - d2_box[0])) // 2, 1805), disc2, fill="#64748B", font=font_disclaimer)
        
        proc.stdin.write(frame.tobytes())
        if frame_idx % 200 == 0:
            print(f"Progres randare: {(frame_idx / total_frames)*100:.1f}%...")
            
    proc.stdin.close()
    _, stderr = proc.communicate()
    if proc.returncode != 0:
        print("Eroare FFmpeg:", stderr.decode("utf-8", errors="ignore"))
        return False
    print(f"✅ Video randat cu succes: {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH)/(1024*1024):.2f} MB)")
    return True

# ── 4. Dispatch Video to Telegram ─────────────────────────────────
def dispatch_to_telegram(scenario, duration):
    print("[4/4] Trimitere videoclip și descriere către Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Atenție: Lipsesc credențialele Telegram.")
        return False

    title = scenario.get("topic_title", "Concursul Național ANFP 2026")
    caption_txt = scenario.get("tiktok_caption", "Testează-ți gratuit pregătirea pe govtalent-romania.vercel.app!")
    
    tg_caption = (
        f"🎬 <b>[GOVTALENT ROMÂNIA • TIKTOK DAILY]</b>\n\n"
        f"📌 <b>Subiect:</b> {title}\n"
        f"⏱ <b>Durată:</b> {duration:.0f}s | Format 9:16 (1080x1920)\n\n"
        f"📋 <b>Descriere recomandată pentru TikTok / Reels (Copy-Paste):</b>\n"
        f"<i>\"{caption_txt}\"</i>\n\n"
        f"👉 <i>Apasă pe video ➔ Partajează / Descarcă ➔ Postare directă în TikTok!</i>"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(VIDEO_PATH, "rb") as vf:
        files = {"video": ("govtalent_tiktok_daily.mp4", vf, "video/mp4")}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": tg_caption,
            "parse_mode": "HTML",
            "supports_streaming": True
        }
        res = requests.post(url, data=data, files=files, timeout=90)
        
    res_json = res.json()
    if res_json.get("ok"):
        print("✅ Videoclipul a fost expediat cu succes pe telefonul tău via Telegram!")
        return True
    else:
        print(f"❌ Eroare Telegram: {res_json.get('description')}")
        return False

# ── Main Entrypoint ───────────────────────────────────────────────
async def main():
    scenario = generate_scenario_with_gemini()
    words, duration = await generate_audio_and_timestamps(scenario["script_speech"])
    success = render_video(scenario, words, duration)
    if success:
        dispatch_to_telegram(scenario, duration)

if __name__ == "__main__":
    asyncio.run(main())
