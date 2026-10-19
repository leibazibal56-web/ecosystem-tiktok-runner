# -*- coding: utf-8 -*-
"""
CarierăStart TikTok Daily Video Generator
- Generates 9:16 vertical videos (1080x1920) with Gemini TTS warm female voice (Aoede) & dynamic word-level subtitles.
- Uses Gemini to synthesize fresh, high-impact career advice for Romanian university graduates entering the private sector.
- Dispatches final MP4 video and copy-paste caption directly to the Telegram bot.
- Runs locally on Windows and automatically via GitHub Actions (Ubuntu).
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

# ── Credențiale & Configurație ────────────────────────────────────
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "8867321650").strip()
GEMINI_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
APP_URL = os.getenv("APP_URL") or "https://cariera-pro-romania.vercel.app/"

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "video-generator"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "cariera_audio.wav")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "cariera_privat_tiktok.mp4")

# ── Fallback Topics (Career & Job Market Romania 2026) ────────────
FALLBACK_TOPICS = [
    {
        "topic_title": "3 GREȘELI ÎN CV CARE TE PICĂ ÎN 6 SECUNDE",
        "alert_badge": "FILTRELE ATS & CV",
        "script_speech": "Ești proaspăt absolvent și nu te sună nimeni la interviu? Recrutorii scanează CV-ul în șase secunde, iar filtrele A T S elimină dosarele prost formatate! Greșeala unu: Barele procentuale de evaluare a abilităților. Softul le vede ca erori de parsare. Greșeala doi: Descrieri pasive fără cifre. Nu scrie am ajutat la proiecte, ci am analizat cinci mii de tranzacții. Greșeala trei: CV mai lung de o pagină. Construiește-ți gratuit un CV compatibil A T S pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "DE CE EȘTI RESPINS ÎN 6 SECUNDE", "color": "#EF4444"},
            {"time_max": 14.0, "text": "1 • GRAFICE PROCENTUALE DE SKILLS", "color": "#F59E0B"},
            {"time_max": 21.5, "text": "2 • DESCRIERI FĂRĂ REZULTATE CUANTIFICATE", "color": "#3B82F6"},
            {"time_max": 27.5, "text": "3 • CV PESTE O SINGURĂ PAGINĂ", "color": "#EF4444"},
            {"time_max": 99.0, "text": "SOLUȚIE • GENERATOR ATS 100% CONFORM", "color": "#10B981"}
        ],
        "tiktok_caption": "Știai că softurile ATS elimină peste 70% din CV-uri înainte să ajungă la un om? 3 greșeli majore pe care le fac tinerii absolvenți. Generează un CV conform pe https://cariera-pro-romania.vercel.app/ ! 📄💼 #absolvent #cv #angajare #primuljob #interviu #carieraprivat #romania"
    },
    {
        "topic_title": "MIT SAU REALITATE: MAI MERITĂ SĂ CAUȚI JOB REMOTE CA DEBUTANT?",
        "alert_badge": "MIT VS REALITATE",
        "script_speech": "Crezi că după facultate vei prinde ușor un job o sută la sută de acasă? Realitatea pieței din România te va surprinde! Posturile exclusiv remote reprezintă doar patru la sută din totalul ofertelor, dar atrag treisprezece la sută din aplicări, adică o concurență de peste trei ori mai acerbă. În schimb, peste nouăzeci și cinci la sută din companii solicită regim hibrid sau prezență la birou pentru mentorat operațional. Calculează-ți salariul real pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "ILUZIA JOBULUI REMOTE", "color": "#EF4444"},
            {"time_max": 13.5, "text": "DOAR 4% DIN OFERTE SUNT REMOTE", "color": "#F59E0B"},
            {"time_max": 20.5, "text": "CONCURENȚĂ DE 3.25X MAI MARE", "color": "#DC2626"},
            {"time_max": 27.0, "text": ">95% ANGAJATORI CER HIBRID/ON-SITE", "color": "#3B82F6"},
            {"time_max": 99.0, "text": "SOLUȚIE • RADAR SALARIAL REGIONAL", "color": "#10B981"}
        ],
        "tiktok_caption": "Mitul jobului full-remote pentru debutanți! De ce concurența e uriașă și unde sunt de fapt oportunitățile reale în 2026. Explorează ghidul pe https://cariera-pro-romania.vercel.app/ ! 🏢📊 #munca #remote #hibrid #salariu #absolventi #studenti #romania"
    },
    {
        "topic_title": "ARGUMENTUL SECRET DE NEGOCIERE: PRIMA DE 4.586 LEI",
        "alert_badge": "LEGEA 176/2018",
        "script_speech": "Faci un internship și vrei să fii angajat definitiv? Iată asul din mânecă pe care nouăzeci la sută dintre debutanți nu îl știu! Conform articolului nouăsprezece din Legea o sută șaptezeci și șase pe două mii optsprezece, compania care semnează contract de muncă cu un intern și îl menține douăzeci și patru de luni primește o primă nerambursabilă de patru mii cinci sute optzeci și șase de lei de la stat. Menționează asta la interviu! Textul exact de negociere este pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "CUM NEGOCIEZI CONTRACTUL DUPĂ STAGIU", "color": "#F59E0B"},
            {"time_max": 14.0, "text": "LEGEA 176/2018 • ARTICOLUL 19", "color": "#3B82F6"},
            {"time_max": 21.5, "text": "4.586 LEI PRIMĂ NERAMBURSABILĂ PENTRU FIRMĂ", "color": "#10B981"},
            {"time_max": 27.5, "text": "AVANTAJUL TĂU DE CONVINGERE", "color": "#2563EB"},
            {"time_max": 99.0, "text": "SOLUȚIE • COPIAZĂ PITCH-UL DE NEGOCIERE", "color": "#10B981"}
        ],
        "tiktok_caption": "Secretul din legea internshipului care te ajută să fii angajat definitiv! Angajatorul primește 4.586 lei de la stat. Folosește pitch-ul de negociere pe https://cariera-pro-romania.vercel.app/ ! 💰🤝 #internship #angajare #negociere #drepturilamunca #student #carieraprivat"
    },
    {
        "topic_title": "ATENȚIE: AI 60 DE ZILE PENTRU PRIMA DE INSERȚIE DE LA ANOFM",
        "alert_badge": "LEGEA 76/2002",
        "script_speech": "Ai terminat facultatea anul acesta? Nu rata banii gratuiți la care ai dreptul legal! Conform Legii șaptezeci și șase pe două mii doi, dacă te înregistrezi la agenția de șomaj în termen strict de șaizeci de zile de la absolvire și te angajezi cu normă întreagă, primești prima de inserție direct în contul tău bancar. Banii se acordă în două tranșe de cincizeci la sută. Verifică dacă mai ești în termen pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "BANI DE LA STAT LA PRIMUL JOB", "color": "#10B981"},
            {"time_max": 13.5, "text": "TERMEN STRICT: 60 ZILE DE LA ABSOLVIRE", "color": "#DC2626"},
            {"time_max": 20.5, "text": "ÎNREGISTRARE OBLIGATORIE LA ANOFM", "color": "#F59E0B"},
            {"time_max": 27.0, "text": "DOUĂ TRANȘE DE PLATĂ ÎN CONTUL TĂU", "color": "#3B82F6"},
            {"time_max": 99.0, "text": "SOLUȚIE • VERIFICĂ-ȚI TERMENUL RAPID", "color": "#10B981"}
        ],
        "tiktok_caption": "Nu pierde prima de inserție de la stat! Fereastra critică de 60 de zile de la absolvire. Calculează-ți termenul pe https://cariera-pro-romania.vercel.app/ ! 🕒💵 #anofm #primadeinsertie #absolvent #facultate #studenti #bani #romania"
    },
    {
        "topic_title": "REGULA CELOR 3 NUMERE CÂND NEGOCIEZI SALARIUL",
        "alert_badge": "NEGOCIERE SALARIU",
        "script_speech": "Ești la interviu și te întreabă ce salariu dorești? Nu da o singură cifră la întâmplare! Folosește regula celor trei numere din ghidul CarierăStart. Unu: Pragul minim de subzistență, calculat în privat ca să-ți acopere chiria și masa. Doi: Ținta realistă de piață, documentată din grilele locale. Trei: Ținta ambițioasă ca ancoră de negociere. Când ești întrebat, oferă un interval net și întreabă de pachetul total: tichete de masă și asigurare. Calculează-ți numerele pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "CE RĂSPUNZI LA: CE SALARIU VREI?", "color": "#F59E0B"},
            {"time_max": 13.5, "text": "1 • PRAGUL MINIM (CHIRIE & CHELTUIELI)", "color": "#EF4444"},
            {"time_max": 20.5, "text": "2 • ȚINTA REALISTĂ MEDIANĂ DE PIAȚĂ", "color": "#3B82F6"},
            {"time_max": 27.0, "text": "3 • ȚINTA AMBIȚIOASĂ (ANCORA)", "color": "#10B981"},
            {"time_max": 99.0, "text": "SOLUȚIE • CALCULATOR PACHET TOTAL", "color": "#10B981"}
        ],
        "tiktok_caption": "Cum răspunzi la întrebarea 'Ce salariu dorești?' la primul job? Regula celor 3 numere și pachetul total. Intră pe https://cariera-pro-romania.vercel.app/ ! 💵🤝 #salariu #negociere #interviu #primuljob #angajare #absolvent"
    },
    {
        "topic_title": "3 SEMNE DE ALARMĂ LA INTERVIU: NU SEMNA!",
        "alert_badge": "RED FLAGS & LEGE",
        "script_speech": "Atenție la primul tău loc de muncă! Iată trei semnale de alarmă clare care ascund abuzuri. Semnalul unu: Ți se cer bani în avans pentru procesare sau uniforme. Este o tentativă de fraudă. Semnalul doi: Ți se spune vino de mâine, semnăm contractul peste două săptămâni. Muncă la negru fără asigurare. Semnalul trei: Proba de lucru durează zeci de ore neplătite pentru a înlocui munca unui angajat. Verifică contractul în registrul oficial pe cariera-pro-romania.vercel.app!",
        "sections": [
            {"time_max": 6.5, "text": "3 SEMNALE DE ALARMĂ LA ANGAJARE", "color": "#DC2626"},
            {"time_max": 13.5, "text": "1 • BANI CERUȚI PENTRU ANGAJARE", "color": "#EF4444"},
            {"time_max": 20.5, "text": "2 • ÎNCEPE MÂINE, SEMNĂM MAI ÎNCOLO", "color": "#F59E0B"},
            {"time_max": 27.0, "text": "3 • PROBE URIAȘE DE MUNCĂ NEPLĂTITĂ", "color": "#DC2626"},
            {"time_max": 99.0, "text": "SOLUȚIE • SCANNER RED FLAGS & REGES", "color": "#10B981"}
        ],
        "tiktok_caption": "Nu cădea în capcanele angajatorilor abuzivi! 3 semnale de alarmă pe care orice debutant trebuie să le știe. Regula celor 3 verificări pe https://cariera-pro-romania.vercel.app/ ! 🛡️⚖️ #redflags #drepturi #codulmuncii #angajare #primuljob #munca"
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
        "name": "TOP 3 CAPCANE / GREȘELI FRECVENTE LA ANGAJARE",
        "instruction": (
            "FORMATUL 1: TOP 3 CAPCANE / GREȘELI FRECVENTE LA PRIMUL JOB. "
            "Structură: Începe cu un Hook alert (primele 4 secunde) despre de ce absolvenții sunt respinși la interviuri sau de ce CV-urile lor sunt ignorate de ATS. "
            "Urmează 3 puncte numerotate Unu / Doi / Trei (solide, concise, cu impact direct) "
            "și un îndemn final de testare pe https://cariera-pro-romania.vercel.app/."
        ),
        "section_structure": "Secțiunea 1 (problemă #DC2626), Punctul 1 (#2563EB), Punctul 2 (#D97706), Punctul 3 (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "myth_vs_reality",
        "name": "MIT VS. REALITATE PE PIAȚA MUNCII DIN ROMÂNIA",
        "instruction": (
            "FORMATUL 2: MIT VS. REALITATE (Munca remote, salarii debutanți, transparență salarială Directiva UE 2023/970). "
            "Structură: Începe cu o întrebare provocatoare sau un mit larg răspândit ('Crezi că la primul job contează notele din facultate? Total fals!'). "
            "Explică de ce este greșit ce crede majoritatea, oferă perspectiva corectă a recrutorilor "
            "și un îndemn final de verificare pe https://cariera-pro-romania.vercel.app/."
        ),
        "section_structure": "Secțiunea 1 (titlu mit #EF4444), De ce e fals (#F59E0B), Realitatea corectă (#2563EB), Regula de aur (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "case_study",
        "name": "STUDIU DE CAZ / SIMULARE INTERVIU METODA STAR",
        "instruction": (
            "FORMATUL 3: STUDIU DE CAZ / SITUAȚIE CONCRETĂ LA INTERVIU. "
            "Structură: Începe cu o dilemă practică de interviu ('Ce răspunzi când recrutorul te întreabă: Povestește-mi despre cel mai mare eșec al tău?'). "
            "Prezintă greșeala tipică pe care o fac debutanții (defensivitate sau scuze), soluția salvatoare folosind metoda STAR la persoana I singular "
            "și îndemnul de a simula pe https://cariera-pro-romania.vercel.app/."
        ),
        "section_structure": "Secțiunea 1 (întrebare interviu #DC2626), Greșeala comună (#F59E0B), Răspunsul STAR corect (#2563EB), Concluzie (#DC2626), CTA final (#10B981)."
    },
    {
        "id": "quick_audit",
        "name": "GHID RAPID / AUDIT ÎN 60 DE SECUNDE AL CV-ULUI",
        "instruction": (
            "FORMATUL 4: GHID RAPID / TEST DE VERIFICARE ÎN 60 SECUNDE PENTRU CV SAU PERIOADA DE PROBĂ (Art. 31 Codul Muncii). "
            "Structură: Începe cu 'Fă acest test rapid în 3 pași înainte să trimiți CV-ul / înainte de perioada de probă de 90 de zile...'. "
            "Prezintă pasul 1, pasul 2 și regula decisivă (pasul 3), "
            "urmat de îndemnul de verificare pe https://cariera-pro-romania.vercel.app/."
        ),
        "section_structure": "Secțiunea 1 (titlu test #3B82F6), Pasul 1 (#2563EB), Pasul 2 (#F59E0B), Pasul 3 (#DC2626), CTA final (#10B981)."
    }
]

def generate_scenario_with_gemini():
    import datetime
    day_idx = datetime.datetime.now().timetuple().tm_yday % len(ROTATING_FORMATS)
    chosen_format = ROTATING_FORMATS[day_idx]
    print(f"[1/4] Solicitare scenariu nou prin Gemini (Format: {chosen_format['name']})...")

    if not GEMINI_KEY:
        return FALLBACK_TOPICS[day_idx % len(FALLBACK_TOPICS)]

    prompt = (
        f"Ești scenaristul oficial pentru conținutul video scurt (TikTok / Reels) al platformei CarierăStart (https://cariera-pro-romania.vercel.app/) - ghid strategic și analitic pentru tinerii absolvenți de facultate (ASE, Politehnică, Drept, Litere, Științe) care vor un job competitiv în mediul privat din România.\n\n"
        f"NORME OBLIGATORII PRIVIND LIMBA ROMÂNĂ (DOOM3 / ACADEMIA ROMÂNĂ):\n"
        f"- Folosește EXCLUSIV LIMBA ROMÂNĂ OFICIALĂ LITERARĂ, conform normelor ortografice oficiale (DOOM3).\n"
        f"- Este STRICT INTERZISĂ orice greșeală de ortografie sau fonetizare greșită (folosește diacritice corecte: ă, â, î, ș, ț).\n"
        f"- Textul trebuie să fie redactat impecabil din punct de vedere gramatical, alert și energic.\n\n"
        f"Astăzi vei crea un scenariu conform acestui stil narativ obligatoriu:\n"
        f"{chosen_format['instruction']}\n\n"
        f"Ghidaj secțiuni grafice: {chosen_format['section_structure']}\n"
        f"Teme cheie: filtrele ATS, metoda STAR, negocierea salariului, Directiva Transparenței Salariale 2023/970, Legea 176/2018 (internship și prima de 4.586 lei din art. 19), Legea 76/2002 (prima de inserție ANOFM în 60 zile), perioada de probă de 90 zile conform Art. 31 Codul Muncii.\n\n"
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
        '  "tiktok_caption": "Descriere captivantă pentru TikTok incluzând linkul https://cariera-pro-romania.vercel.app/ și hashtag-uri relevante: #absolvent #job #interviu #carieraprivat #salariu #studenti #cv #romania"\n'
        "}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
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

# ── 2. Romanian Neural Audio (Gemini Aoede Warm Female Voice) ─────
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
    print("[2/4] Generare voce feminină fermecătoare, caldă & sigură (Gemini Aoede)...")
    import base64
    import wave
    import time

    tts_models = [
        "gemini-3.1-flash-tts-preview",
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts"
    ]

    prompt = (
        f"""Citește cu o voce feminină deosebit de fermecătoare, caldă, foarte melodioasă, energică, sigură și perfect naturală în limba română următorul ghid de carieră profesională:

{script_text}"""
    )

    if GEMINI_KEY:
        for model in tts_models:
            for attempt in range(4):
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
                        print(f"✅ Voce feminină Aoede generată cu succes prin {model}: {len(pcm)} bytes, durată {duration:.2f}s, {len(words)} cuvinte sincronizate.")
                        return words, duration, wav_path
                    elif res.status_code in (429, 503):
                        wait_sec = 6 * (attempt + 1)
                        print(f"Modelul {model} a returnat {res.status_code}. Așteptare {wait_sec}s pentru cotă...")
                        time.sleep(wait_sec)
                    else:
                        print(f"Modelul {model} a returnat status {res.status_code}. Se trece la următorul...")
                        break
                except Exception as e:
                    print(f"Avertisment generare voce cu {model} (încercarea {attempt+1}): {e}.")
                    time.sleep(5)

    # Fallback Edge-TTS
    print("[Fallback de urgență] Folosire Edge-TTS cu vocea ro-RO-AlinaNeural...")
    import edge_tts
    phonetic_map = {
        "online": "onlain", "site": "sait", "site-ul": "saitul",
        "feedback": "fidbac", "job": "giob", "AI": "A I", "ATS": "A T S", "BPO": "B P O", "SSC": "S S C"
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
            
    fallback_audio = AUDIO_PATH
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
            "end": current_phrase[-1]["end"] + 0.25
        })
    return phrases

def render_video(scenario, words, total_duration, audio_path):
    print(f"[3/4] Randare video vertical 9:16 (1080x1920, {total_duration:.1f}s) cu FFmpeg...")
    width, height = 1080, 1920
    fps = 30
    total_frames = int(total_duration * fps)
    
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
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
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        VIDEO_PATH
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    font_badge = get_font(32, bold=True)
    font_title = get_font(52, bold=True)
    font_section = get_font(42, bold=True)
    font_word = get_font(72, bold=True)
    font_word_sm = get_font(58, bold=True)
    font_cta = get_font(44, bold=True)
    font_cta_sub = get_font(32, bold=False)
    font_disclaimer = get_font(24, bold=False)
    
    def get_w_font(txt):
        return font_word_sm if len(txt) > 8 else font_word

    title_text = scenario.get("topic_title", "GHID CARIERĂ PRIVAT ROMÂNIA")
    alert_badge = scenario.get("alert_badge", "INSERȚIE PROFESIONALĂ")
    sections = scenario.get("sections", [])
    phrases = build_phrases(words)
    
    cta_main = "CARIERA-PRO-ROMANIA.VERCEL.APP"
    cta_sub = "ACCESEAZĂ SIMULATOARELE & GHIDUL COMPLET"
    disc1 = "Resursă educațională & metodologică pentru absolvenți"
    disc2 = "Operat legal de TEODORESCU O.DIANA PFA • Nu garantează angajarea"

    # Pre-render Background Frame
    base_img = Image.new("RGB", (width, height), "#0B1329")
    base_draw = ImageDraw.Draw(base_img)
    
    # Elegant Corporate Gradient background
    for y in range(height):
        ratio = y / height
        r = int(11 * (1 - ratio) + 26 * ratio)
        g = int(19 * (1 - ratio) + 41 * ratio)
        b = int(41 * (1 - ratio) + 75 * ratio)
        base_draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Ambient soft circular glow
    base_draw.ellipse([-150, 600, 450, 1200], fill=(20, 40, 85))
    base_draw.ellipse([width - 400, 900, width + 200, 1500], fill=(15, 35, 75))

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_img.copy()
        draw = ImageDraw.Draw(frame)
        
        # 1. Header Badge & Title
        b_box = draw.textbbox((0, 0), alert_badge, font=font_badge)
        b_w = b_box[2] - b_box[0]
        b_pad_x, b_pad_y = 28, 12
        b_x = (width - (b_w + b_pad_x * 2)) // 2
        draw.rounded_rectangle([b_x, 110, b_x + b_w + b_pad_x * 2, 110 + 52], radius=16, fill="#1E3A8A", outline="#3B82F6", width=2)
        draw.text((b_x + b_pad_x, 118), alert_badge, fill="#93C5FD", font=font_badge)
        
        # Title wrap
        t_words = title_text.split()
        t_lines = []
        cur_l = []
        for w in t_words:
            test_l = " ".join(cur_l + [w])
            box = draw.textbbox((0, 0), test_l, font=font_title)
            if box[2] - box[0] <= width - 140:
                cur_l.append(w)
            else:
                if cur_l:
                    t_lines.append(" ".join(cur_l))
                cur_l = [w]
        if cur_l:
            t_lines.append(" ".join(cur_l))
            
        t_y = 185
        for l in t_lines:
            l_box = draw.textbbox((0, 0), l, font=font_title)
            l_w = l_box[2] - l_box[0]
            draw.text(((width - l_w) // 2 + 2, t_y + 2), l, fill="#000000", font=font_title)
            draw.text(((width - l_w) // 2, t_y), l, fill="#FFFFFF", font=font_title)
            t_y += 64
            
        # 2. Dynamic Section Indicator Card
        sec_text = "GHID OPERAȚIONAL"
        sec_color = "#3B82F6"
        for s in sections:
            if t <= s.get("time_max", 999):
                sec_text = s.get("text", sec_text)
                sec_color = s.get("color", sec_color)
                break
                
        sec_box = draw.textbbox((0, 0), sec_text, font=font_section)
        sec_w = sec_box[2] - sec_box[0]
        draw.rounded_rectangle([(width - sec_w) // 2 - 32, 320, (width + sec_w) // 2 + 32, 385], radius=16, fill=sec_color)
        draw.text(((width - sec_w) // 2, 328), sec_text, fill="#FFFFFF", font=font_section)
        
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
            
        # 5. Call To Action Box
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

    title = scenario.get("topic_title", "Ghid Inserție Profesională Absolvenți")
    caption_txt = scenario.get("tiktok_caption", f"Accesează ghidul complet pe {APP_URL} !")
    
    tg_caption = (
        f"💼 <b>[CARIERĂSTART TIKTOK DAILY]</b>\n\n"
        f"📌 <b>Subiect:</b> {title}\n"
        f"⏱ <b>Durată:</b> {duration:.0f}s | Format 9:16 (1080x1920)\n\n"
        f"📋 <b>Atinge textul din caseta de mai jos</b> <i>(se copiază automat în clipboard pe telefon):</i>\n\n"
        f"<code>{caption_txt}</code>\n\n"
        f"👉 <i>Apasă pe video ➔ Salvează / Descarcă ➔ Lipește descrierea direct în TikTok / Reels / Shorts!</i>"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(VIDEO_PATH, "rb") as vf:
        files = {"video": ("cariera_privat_tiktok.mp4", vf, "video/mp4")}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": tg_caption,
            "parse_mode": "HTML",
            "supports_streaming": True
        }
        res = requests.post(url, data=data, files=files, timeout=90)
        
    res_json = res.json()
    if res_json.get("ok"):
        print("✅ Videoclipul CarierăStart a fost expediat cu succes pe Telegram!")
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
