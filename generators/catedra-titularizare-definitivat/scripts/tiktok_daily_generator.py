# -*- coding: utf-8 -*-
"""
EduTitularizare - TikTok & Reels Daily Video Generator
======================================================
Modul: scripts/tiktok_daily_generator.py

Funcționalități:
1. Generare videoclipuri verticale 9:16 (1080x1920) cu subtitrări animate sincronizate (karaoke highlight).
2. Voce umană, caldă, feminină și atractivă (Gemini TTS Aoede / Edge-TTS ro-RO-AlinaNeural cu dicționar fonetic).
3. 4 Formate narative rotative de mare impact pentru candidații la Titularizare & Definitivat.
4. Generare scenarii noi zilnice prin Gemini 2.5 Flash, cu fallback-uri de calitate superioară gata pregătite.
5. Livrare automată directă pe canalul / chat-ul de Telegram al administratorului cu casetă 'click-to-copy'.
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

# ── Credențiale & Configurare ─────────────────────────────────────────────
GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "8867321650").strip()

OUTPUT_DIR = os.path.abspath(os.path.join(ROOT_DIR, "video-generator"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "daily_audio.wav")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "edutitularizare_tiktok.mp4")

# ── 4 Scenarii Fallback de Calitate Superioară (Titularizare & Definitivat) ─
FALLBACK_TOPICS = [
    {
        "topic_title": "3 GREȘELI FATALE LA PROBA SCRISĂ DE TITULARIZARE",
        "alert_badge": "TITULARIZARE 2026",
        "script_speech": "Dai Titularizarea sau Definitivatul anul acesta? Iată trei greșeli care te pot costa titularizarea! Unu: Blocarea excesivă pe Subiectul întâi. Dacă aloci mai mult de două ore specialității, nu mai ai timp pentru pedagogie și metodică. Doi: Verbele pasive la obiective operaționale. Dacă scrii 'elevul să înțeleagă', ești depunctat instant! Folosește verbe măsurabile conform Robert Mager. Trei: Absența baremului analitic la proiectare. Testează-ți eseurile gratuit pe titularizare-si-definitivat.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "GREȘELI SCRIS TITULARIZARE", "color": "#DC2626"},
            {"time_max": 14.5, "text": "1 • BLOCAJUL DE TIMP SUBIECTUL 1", "color": "#2563EB"},
            {"time_max": 22.5, "text": "2 • VERBELE PASIVE INTERZISE", "color": "#D97706"},
            {"time_max": 28.5, "text": "3 • BAREMUL ANALITIC LIPSĂ", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • SIMULATOR PE BAREM", "color": "#10B981"}
        ],
        "tiktok_caption": "Nu pierde catedra de titular din cauza gestiunii timpului sau a verbelor pasive! 3 greșeli majore conform metodologiei ME. Antrenează-te pe https://titularizare-si-definitivat.vercel.app ! 📚👩‍🏫 #titularizare #definitivat #profesori #invatamant #edutitularizare #educatie #scoala"
    },
    {
        "topic_title": "MIT SAU REALITATE: NOTA 7 ÎȚI ASIGURĂ POSTUL PE VIAȚĂ?",
        "alert_badge": "MIT VS REALITATE",
        "script_speech": "Crezi că dacă iei nota șapte la concursul național devii automat titular pe viață? Total fals! Baremul legal cere nota șapte, însă titularizarea pe perioadă nedeterminată este posibilă doar dacă postul are viabilitate de minim patru ani școlari. Dacă postul are viabilitate de unu până la trei ani, vei fi încadrat exclusiv ca suplinitor! Calculează-ți media de repartizare și verifică viabilitatea posturilor pe titularizare-si-definitivat.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "MITUL NOTEI 7 LA CONCURS", "color": "#EF4444"},
            {"time_max": 14.0, "text": "VIABILITATEA MINIM 4 ANI", "color": "#F59E0B"},
            {"time_max": 21.5, "text": "1-3 ANI: DOAR SUPLINIRE", "color": "#2563EB"},
            {"time_max": 27.5, "text": "MEDIA MR: 75% SCRIS + 25% PRACTICĂ", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • CALCULATOR OFICIAL MR", "color": "#10B981"}
        ],
        "tiktok_caption": "Cât valorează nota 7 la Titularizare dacă postul nu este viabil 4 ani? Află diferența critică dintre titularizare și suplinire! Verifică pe https://titularizare-si-definitivat.vercel.app ! 🏫🎓 #titularizare2026 #profesori #viabilitate #suplinitor #edutitularizare #scoala"
    },
    {
        "topic_title": "ATENȚIE LA DEFINITIVAT: BLOCAT ÎNAINTE DE PROBA SCRISĂ!",
        "alert_badge": "DEFINITIVAT OME 3858",
        "script_speech": "Te pregătești pentru examenul de Definitivat? Atenție la regula eliminatorie din noul ordin de ministru! Nu ai voie să intri în sala de examen scris dacă media celor două inspecții și a portofoliului este sub nota opt, sau dacă ai obținut chiar și un singur șapte virgulă nouăzeci și nouă la o inspecție. O singură notă sub șapte te descalifică automat! Descarcă șabloanele celor cinci piese de portofoliu de pe titularizare-si-definitivat.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "ELIMINARE LA DEFINITIVAT", "color": "#DC2626"},
            {"time_max": 14.0, "text": "CONDITIA 1: MEDIA MINIM 8.00", "color": "#F59E0B"},
            {"time_max": 21.5, "text": "CONDITIA 2: NICIO NOTĂ SUB 7.00", "color": "#2563EB"},
            {"time_max": 27.5, "text": "OME 3858/2026: CELE 5 PIESE", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • PORTOFOLIU OFICIAL", "color": "#10B981"}
        ],
        "tiktok_caption": "Știai că poți fi blocat de la proba scrisă de Definitivat înainte să intri în sală? Condițiile eliminatorii OME 3858/2026 explicate! Descarcă șabloanele pe https://titularizare-si-definitivat.vercel.app ! 📑👩‍🏫 #definitivat #definitivat2026 #portofoliudidactic #profesoridebutanti #edutitularizare"
    },
    {
        "topic_title": "AUDIT ÎN 60 SEC: STRUCTURA LECȚIEI DE NOTA 10",
        "alert_badge": "AUDIT ÎN 60 SECUNDE",
        "script_speech": "Vrei să obții punctaj maxim la proiectarea didactică la Titularizare? Fă acest test rapid în trei pași! Pasul unu: Ai integrat cele nouă evenimente ale instruirii definite de Robert Gagné? Pasul doi: Obiectivele tale operaționale conțin comportamentul observabil și criteriul de reușită conform lui Mager? Pasul trei: Ai corelat fiecare secvență cu o metodă activă și un instrument de evaluare formativă? Evaluează-ți proiectele pe titularizare-si-definitivat.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "TESTUL PROIECTĂRII DE NOTA 10", "color": "#3B82F6"},
            {"time_max": 13.5, "text": "1 • EVENIMENTELE LUI GAGNE", "color": "#2563EB"},
            {"time_max": 20.5, "text": "2 • VERBE MĂSURABILE MAGER", "color": "#F59E0B"},
            {"time_max": 27.0, "text": "3 • EVALUARE FORMATIVĂ", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • EVALUATOR DIDACTIC AI", "color": "#10B981"}
        ],
        "tiktok_caption": "Cum arată proiectul didactic de nota 10 la Titularizare? Verifică-ți planificarea în 60 de secunde după standardele Robert Gagné și Bloom pe https://titularizare-si-definitivat.vercel.app ! 📝⏱️ #titularizare #didactica #pedagogie #proiectdidactic #edutitularizare #profesori"
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
        "id": "top3_traps",
        "name": "TOP 3 CAPCANE / GREȘELI FRECVENTE LA EXAMEN",
        "instruction": (
            "FORMATUL 1: TOP 3 CAPCANE / GREȘELI FRECVENTE LA TITULARIZARE SAU DEFINITIVAT. "
            "Structură: Începe cu un Hook alert (primele 4 secunde) despre pericole sau scăpări majore din subiecte sau legislație. "
            "Urmează 3 puncte numerotate Unu / Doi / Trei (solide, concise, cu impact direct pe barem) "
            "și un îndemn final de testare pe https://titularizare-si-definitivat.vercel.app."
        ),
        "section_structure": "Secțiunea 1 (problemă #DC2626), Punctul 1 (#2563EB), Punctul 2 (#D97706), Punctul 3 (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "myth_vs_reality",
        "name": "MIT VS. REALITATE / ADEVĂRAT SAU FALS",
        "instruction": (
            "FORMATUL 2: MIT VS. REALITATE / ADEVĂRAT SAU FALS. "
            "Structură: Începe cu o întrebare provocatoare sau un mit larg răspândit în cancelarii ('Crezi că...? Total fals!'). "
            "Explică de ce este greșit ce crede majoritatea profesorilor debutanți, oferă perspectiva legală exactă (Legea 198/2023 sau OME 3858/2026) "
            "și un îndemn final de verificare pe https://titularizare-si-definitivat.vercel.app."
        ),
        "section_structure": "Secțiunea 1 (titlu mit #EF4444), De ce e fals (#F59E0B), Realitatea corectă (#2563EB), Regula de aur (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "case_study",
        "name": "STUDIU DE CAZ / SITUAȚIE CONCRETĂ DE EXAMEN",
        "instruction": (
            "FORMATUL 3: STUDIU DE CAZ / SITUAȚIE CONCRETĂ. "
            "Structură: Începe cu o dilemă practică sau docimologică din sala de examen ('Ce faci dacă te confrunți cu...?'). "
            "Prezintă greșeala tipică la inspecție sau la scris, pasul salvator sau soluția metodică corectă "
            "și îndemnul de a simula pe https://titularizare-si-definitivat.vercel.app."
        ),
        "section_structure": "Secțiunea 1 (dilemă #DC2626), Greșeala comună (#F59E0B), Soluția pas cu pas (#2563EB), Concluzie (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "quick_audit",
        "name": "GHID RAPID / AUDIT ÎN 60 DE SECUNDE",
        "instruction": (
            "FORMATUL 4: GHID RAPID / TEST DE VERIFICARE ÎN 60 SECUNDE. "
            "Structură: Începe cu 'Fă acest test rapid în 3 pași înainte să predai lucrarea/portofoliul...'. "
            "Prezintă pasul 1, pasul 2 și regula decisivă (pasul 3), "
            "urmat de îndemnul de verificare pe https://titularizare-si-definitivat.vercel.app."
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
        f"Ești scenaristul oficial pentru conținutul video scurt (TikTok / Reels / YouTube Shorts) al platformei EduTitularizare (https://titularizare-si-definitivat.vercel.app) - platforma națională de pregătire pentru Concursul de Titularizare și Examenul de Definitivat, bazată pe Legea învățământului preuniversitar nr. 198/2023 și Ordinul de ministru nr. 3858/2026.\n\n"
        f"NORME OBLIGATORII PRIVIND LIMBA ROMÂNĂ (DOOM3 / ACADEMIA ROMÂNĂ):\n"
        f"- Folosește EXCLUSIV LIMBA ROMÂNĂ OFICIALĂ LITERARĂ, conform normelor ortografice, ortoepice și morfologice oficiale (DOOM3).\n"
        f"- Este STRICT INTERZISĂ orice greșeală gramaticală sau ortografică (folosește diacritice corecte: ă, â, î, ș, ț).\n"
        f"- Tonul este cald, profesionist, încurajator, captivant și adaptat cadrelor didactice.\n\n"
        f"Astăzi vei crea un scenariu conform acestui stil narativ obligatoriu:\n"
        f"{chosen_format['instruction']}\n\n"
        f"Ghidaj secțiuni grafice: {chosen_format['section_structure']}\n"
        f"Domenii recomandate: Concursul Național de Titularizare (gestiunea celor 240 minute, barem metodică, obiective Robert Mager, viabilitate posturi 4 ani), Examenul de Definitivat (cele 5 piese de portofoliu OME 3858/2026, media eliminatorie minim 8.00), probele practice (cele 8 anexe).\n\n"
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
        '  "tiktok_caption": "Descriere captivantă pentru TikTok incluzând linkul https://titularizare-si-definitivat.vercel.app și 4-6 hashtag-uri relevante: #titularizare #definitivat #profesori #invatamant #edutitularizare #educatie"\n'
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


# ── 2. Generare Voce Umană, Caldă, Feminină & Atractivă ────────────────────
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
        f"""Citește cu o voce feminină deosebit de fermecătoare, caldă, foarte melodioasă, empatică, sigură și perfect naturală în limba română următorul ghid educațional dedicat cadrelor didactice:

{script_text}"""
    )

    if GEMINI_API_KEY:
        for model in tts_models:
            for attempt in range(3):
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
                        print(f"✅ Voce feminină Aoede (caldă & atractivă) generată cu succes prin {model}: {len(pcm)} bytes, durată {duration:.2f}s.")
                        return words, duration, wav_path
                    elif res.status_code in (429, 503):
                        wait_sec = 4 * (attempt + 1)
                        print(f"Modelul {model} ocupat ({res.status_code}). Așteptare {wait_sec}s...")
                        time.sleep(wait_sec)
                    else:
                        break
                except Exception as e:
                    print(f"Avertisment apel TTS {model}: {e}")
                    time.sleep(3)

    # Fallback de elită Edge-TTS ro-RO-AlinaNeural cu dicționar fonetic profesional
    print("[Fallback de excelență] Generare voce feminină prin Edge-TTS (ro-RO-AlinaNeural - caldă & naturală)...")
    import edge_tts
    phonetic_map = {
        "online": "onlain", "site": "sait", "site-ul": "saitul",
        "feedback": "fidbac", "job": "giob", "AI": "A I", "BAC": "Bac",
        "OME": "O M E", "ISJ": "I S J", "DPPD": "D P P D", "CNPEE": "C N P E E",
        "SSM": "S S M", "VET": "V E T", "TIC": "T I C", "Gagné": "Ganie",
        "Gagne": "Ganie", "Mager": "Meigher", "Bloom": "Blum", "MR": "M R",
        "ND": "N D", "NS": "N S", "NP": "N P", "NI1": "N I 1", "NI2": "N I 2",
        "titularizare-si-definitivat.vercel.app": "titularizare și definitivat punct versel punct ap",
        "vercel.app": "versel punct ap",
        "vercel": "versel"
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
    print(f"✅ Voce feminină AlinaNeural generată cu succes: durată {duration:.2f}s, {len(words)} cuvinte sincronizate.")
    return words, duration, fallback_audio


# ── 3. Randare Video 1080x1920 (Subtitrări Dinamice Karaoke Highlight) ────
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
    
    # Gradient fundal elegant (Midnight Navy to Slate)
    base_bg = Image.new("RGB", (width, height), "#0B0F19")
    draw_bg = ImageDraw.Draw(base_bg)
    for y in range(height):
        ratio = y / height
        r = int(10 * (1 - ratio) + 15 * ratio)
        g = int(15 * (1 - ratio) + 23 * ratio)
        b = int(35 * (1 - ratio) + 48 * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Card central ambient cu contur indigo fin
    draw_bg.rounded_rectangle([60, 680, width - 60, 1260], radius=40, fill="#0F172A", outline="#1E293B", width=2)
    
    # Fonturi
    font_brand = get_font(34, bold=True)
    font_section = get_font(38, bold=True)
    font_word = get_font(60, bold=True)
    font_word_sm = get_font(38, bold=True)
    font_cta = get_font(27, bold=True)
    font_cta_sub = get_font(26, bold=True)
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
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    brand_text = "EDUTITULARIZARE • TITULARIZARE & DEFINITIVAT"
    cta_main = "Pregătește-te pe titularizare-si-definitivat.vercel.app"
    cta_sub = "+ Urmărește pentru trucuri didactice de nota 10"
    disc1 = "Platformă națională de pregătire conform Legii nr. 198/2023."
    disc2 = "Portofoliu didactic OME nr. 3858/2026 și simulatoare oficiale de examen."
    
    def get_current_section(t):
        for sec in sections:
            if t <= sec.get("time_max", 999):
                return sec.get("text", "TITULARIZARE 2026"), sec.get("color", "#6366F1")
        return "SOLUȚIE • SIMULATOR PE BAREM", "#10B981"
        
    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)
        
        # 1. Top Brand Pill
        pill_w, pill_h = 760, 68
        pill_x = (width - pill_w) // 2
        pill_y = 200
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=34, fill="#1E293B", outline="#6366F1", width=2)
        b_box = draw.textbbox((0, 0), brand_text, font=font_brand)
        draw.text(((width - (b_box[2] - b_box[0])) // 2, pill_y + 16), brand_text, fill="#818CF8", font=font_brand)
        
        # 2. Section Alert Box Dinamic
        sec_text, sec_color = get_current_section(t)
        sec_bbox = draw.textbbox((0, 0), sec_text, font=font_section)
        sec_w = sec_bbox[2] - sec_bbox[0]
        s_pad = 28
        draw.rounded_rectangle(
            [(width - sec_w)//2 - s_pad, 315, (width + sec_w)//2 + s_pad, 385],
            radius=16,
            fill=sec_color
        )
        draw.text(((width - sec_w) // 2, 326), sec_text, fill="#FFFFFF", font=font_section)
        
        # 3. Dynamic Center Phrase & Word Highlighting Karaoke
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
            spacing = 18
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
                        draw.rounded_rectangle([cur_x - 14, cur_y - 10, cur_x + ww + 14, cur_y + wh + 10], radius=12, fill="#FACC15")
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
                            draw.rounded_rectangle([cur_x - 14, cur_y - 10, cur_x + ww + 14, cur_y + wh + 10], radius=12, fill="#FACC15")
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#000000", font=f_cur)
                        else:
                            draw.text((cur_x + 2, cur_y + 2), w["text"].upper(), fill="#000000", font=f_cur)
                            draw.text((cur_x, cur_y), w["text"].upper(), fill="#FFFFFF", font=f_cur)
                        cur_x += ww + spacing
                    cur_y += 120

        # 4. Progress bar de redare
        progress = min(1.0, t / total_duration)
        bar_left, bar_right = 80, width - 80
        bar_y = 1560
        draw.rounded_rectangle([bar_left, bar_y, bar_right, bar_y + 12], radius=6, fill="#1E293B")
        fill_w = int(bar_left + (bar_right - bar_left) * progress)
        if fill_w > bar_left + 6:
            draw.rounded_rectangle([bar_left, bar_y, fill_w, bar_y + 12], radius=6, fill="#6366F1")
            
        # 5. Call To Action Final
        c1_box = draw.textbbox((0, 0), cta_main, font=font_cta)
        c2_box = draw.textbbox((0, 0), cta_sub, font=font_cta_sub)
        draw.text(((width - (c1_box[2] - c1_box[0])) // 2, 1620), cta_main, fill="#818CF8", font=font_cta)
        draw.text(((width - (c2_box[2] - c2_box[0])) // 2, 1680), cta_sub, fill="#94A3B8", font=font_cta_sub)
        
        # 6. Micro Disclaimer
        d1_box = draw.textbbox((0, 0), disc1, font=font_disclaimer)
        d2_box = draw.textbbox((0, 0), disc2, font=font_disclaimer)
        draw.text(((width - (d1_box[2] - d1_box[0])) // 2, 1770), disc1, fill="#64748B", font=font_disclaimer)
        draw.text(((width - (d2_box[2] - d2_box[0])) // 2, 1805), disc2, fill="#64748B", font=font_disclaimer)
        
        proc.stdin.write(frame.tobytes())
        if frame_idx % 200 == 0:
            print(f"Progres randare video: {(frame_idx / total_frames)*100:.1f}%...")
            
    proc.stdin.close()
    stderr_text = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    proc.wait()
    if proc.returncode != 0:
        print("Eroare FFmpeg:", stderr_text)
        return False
    print(f"✅ Video randat cu succes: {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH)/(1024*1024):.2f} MB)")
    return True


# ── 4. Expediere Videoclip către Telegram ─────────────────────────────────
async def dispatch_to_telegram(scenario, duration):
    print("[4/4] Trimitere videoclip și descriere către Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Atenție: Lipsesc credențialele Telegram.")
        return False

    title = scenario.get("topic_title", "Truc Metodic pentru Titularizare & Definitivat")
    caption_txt = scenario.get("tiktok_caption", "Pregătește-te inteligent pe https://titularizare-si-definitivat.vercel.app !")

    # 1. Încercare prin telegram_publisher dacă este disponibil
    try:
        from services.telegram_publisher import send_video_for_approval
        result = await send_video_for_approval(
            video_path=VIDEO_PATH,
            caption=caption_txt,
            title=title,
            duration=duration,
            bot_token=TELEGRAM_BOT_TOKEN,
            chat_id=TELEGRAM_CHAT_ID
        )
        if result.get("success"):
            print("✅ Videoclipul EduTitularizare a fost expediat spre aprobare pe Telegram!")
            print(f"   Message ID: {result.get('message_id')}")
            return True
        else:
            print(f"[Notice] Fallback direct Telegram API: {result.get('error')}")
    except Exception as e:
        print(f"[Notice] Trimitere directă via Telegram API: {e}")

    # 2. Trimitere directă sigură prin Telegram Bot HTTP API
    try:
        tg_caption = (
            f"🎬 <b>[EDUTITULARIZARE • TIKTOK & REELS DAILY]</b>\n\n"
            f"📌 <b>Subiect:</b> {title}\n"
            f"⏱️ <b>Durată:</b> {duration:.0f}s | Format 9:16 (1080x1920)\n\n"
            f"📋 <b>Atinge textul din caseta de mai jos</b> <i>(se copiază automat în clipboard):</i>\n\n"
            f"<code>{caption_txt}</code>\n\n"
            f"📲 <i>Apasă pe video → Salvează / Descarcă → Lipește descrierea direct în TikTok / Reels!</i>"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        with open(VIDEO_PATH, "rb") as vf:
            files = {"video": ("edutitularizare_tiktok.mp4", vf, "video/mp4")}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": tg_caption,
                "parse_mode": "HTML",
                "supports_streaming": True
            }
            res = requests.post(url, data=data, files=files, timeout=120)
        res_json = res.json()
        if res_json.get("ok"):
            print("✅ Videoclipul EduTitularizare a fost expediat cu succes pe Telegram!")
            return True
        else:
            print(f"❌ Eroare Telegram: {res_json}")
            return False
    except Exception as ex:
        print(f"❌ Eroare la trimiterea pe Telegram: {ex}")
        return False


# ── Punct de Intrare Principal ────────────────────────────────────────────
async def main():
    scenario = generate_scenario_with_gemini()
    words, duration, audio_path = await generate_audio_and_timestamps(scenario["script_speech"])
    success = render_video(scenario, words, duration, audio_path)
    if success:
        await dispatch_to_telegram(scenario, duration)

if __name__ == "__main__":
    asyncio.run(main())
