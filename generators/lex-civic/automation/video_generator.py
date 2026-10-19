# -*- coding: utf-8 -*-
"""
LexCivic TikTok Video Generator Engine
Produce videoclipuri verticale 9:16 (1080x1920) de înaltă rezoluție,
cu narațiune audio generată prin Microsoft Neural TTS (voce română feminină/masculină),
scene vizuale sincronizate, citări legislative oficiale, branding civic și conformitate CAEN 8559.
"""

import sys
import os
import asyncio
import tempfile
import subprocess
import textwrap
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
import edge_tts

# Asigură codificarea UTF-8 pe Windows console
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
VIDEOS_DIR = os.path.join(SCRIPT_DIR, "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

# Găsire fonturi Windows și Linux cu suport diacritice românești
def get_fonts():
    font_bold_candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    font_reg_candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    
    font_bold_path = next((p for p in font_bold_candidates if os.path.exists(p)), None)
    font_reg_path = next((p for p in font_reg_candidates if os.path.exists(p)), None)
    
    def load_font(path, size):
        if path:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        try:
            return ImageFont.load_default(size)
        except Exception:
            return ImageFont.load_default()

    return {
        "title": load_font(font_bold_path, 52),
        "headline": load_font(font_bold_path, 44),
        "badge": load_font(font_bold_path, 28),
        "body": load_font(font_reg_path, 34),
        "body_bold": load_font(font_bold_path, 36),
        "citation": load_font(font_bold_path, 32),
        "cta_url": load_font(font_bold_path, 34),
        "footer": load_font(font_reg_path, 24),
        "footer_bold": load_font(font_bold_path, 28),
    }

class TikTokVideoGenerator:
    def __init__(self, voice: str = "ro-RO-AlinaNeural"):
        self.voice = voice
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.fonts = get_fonts()

    def _draw_rounded_card(self, draw: ImageDraw.Draw, bbox, fill, outline, width=3, radius=30):
        x0, y0, x1, y1 = bbox
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        words = text.split()
        lines = []
        cur_line = []
        for word in words:
            test_line = " ".join(cur_line + [word])
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                cur_line.append(word)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                    cur_line = [word]
                else:
                    lines.append(word)
                    cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))
        return lines

    def render_scene_frame(self, scene: Dict[str, Any], domain: str, scene_idx: int, total_scenes: int) -> Image.Image:
        """Generează o imagine HD 1080x1920 pentru o scenă specifică."""
        width, height = 1080, 1920
        # Fundal gradient modern albastru-închis/indigo
        img = Image.new("RGB", (width, height), (9, 14, 26))
        draw = ImageDraw.Draw(img)

        # Accente grafice circulare subtile în fundal
        draw.ellipse([-150, -150, 450, 450], fill=(16, 28, 54))
        draw.ellipse([700, 1400, 1300, 2000], fill=(14, 24, 46))
        draw.ellipse([800, 200, 1200, 600], fill=(18, 32, 62))

        # 1. HEADER (y: 110 - 240)
        # Pill Header Brand
        header_bbox = [140, 110, 940, 190]
        self._draw_rounded_card(draw, header_bbox, fill=(20, 30, 52), outline=(59, 130, 246), width=3, radius=25)
        draw.text((540, 150), "LEXCIVIC • GHID JURIDIC PRACTIC", font=self.fonts["badge"], fill=(255, 255, 255), anchor="mm")

        # Domeniu Civic Tag
        draw.text((540, 225), f"— {domain.upper()} —", font=self.fonts["footer_bold"], fill=(56, 189, 248), anchor="mm")

        # 2. CARDUL CENTRAL (y: 280 - 1500)
        card_bbox = [80, 280, 1000, 1500]
        self._draw_rounded_card(draw, card_bbox, fill=(17, 24, 39), outline=(37, 99, 235), width=4, radius=40)

        # Badge Tematic Al Scenei (ex: 🚨 ALARMĂ, ⚠️ CLAUZĂ ABUZIVĂ, ⚖️ CODUL PENAL)
        badge_text = scene.get("badge", "INFORMAȚIE JURIDICĂ")
        badge_color = scene.get("badge_color", (239, 68, 68)) # Roșu implicit
        
        badge_bbox = [130, 330, 950, 410]
        self._draw_rounded_card(draw, badge_bbox, fill=badge_color, outline=(255, 255, 255), width=2, radius=20)
        draw.text((540, 370), badge_text, font=self.fonts["badge"], fill=(255, 255, 255), anchor="mm")

        # Titlu / Headline Scenă
        headline_text = scene.get("headline", "")
        headline_lines = self._wrap_text(headline_text, self.fonts["title"], max_width=820)
        cur_y = 460
        for line in headline_lines[:3]:
            draw.text((540, cur_y), line, font=self.fonts["title"], fill=(251, 191, 36), anchor="mm") # Galben auriu
            cur_y += 65

        # Linie Separatoare
        draw.line([130, cur_y + 10, 950, cur_y + 10], fill=(45, 55, 72), width=3)
        cur_y += 45

        # Puncte Cheie / Corp Scenă
        body_points = scene.get("body_points", [])
        if not body_points and "body_text" in scene:
            body_points = [scene["body_text"]]

        for pt in body_points:
            pt_lines = self._wrap_text(pt, self.fonts["body"], max_width=780)
            for line in pt_lines:
                draw.text((140, cur_y), line, font=self.fonts["body"], fill=(243, 244, 246))
                cur_y += 50
            cur_y += 25

        # Caseta Citare Lege / Sancțiune
        citation = scene.get("citation", "")
        if citation:
            cit_bbox = [120, 1310, 960, 1450]
            self._draw_rounded_card(draw, cit_bbox, fill=(24, 34, 58), outline=(245, 158, 11), width=3, radius=25)
            draw.text((540, 1345), "PREVEDERE LEGALĂ OFICIALĂ", font=self.fonts["footer_bold"], fill=(245, 158, 11), anchor="mm")
            
            cit_lines = self._wrap_text(citation, self.fonts["citation"], max_width=780)
            cit_y = 1385
            for line in cit_lines[:2]:
                draw.text((540, cit_y), line, font=self.fonts["citation"], fill=(255, 255, 255), anchor="mm")
                cit_y += 40

        # 3. ZONA FOOTER & CTA (y: 1530 - 1860)
        # CTA Box
        cta_bbox = [80, 1530, 1000, 1720]
        self._draw_rounded_card(draw, cta_bbox, fill=(15, 23, 42), outline=(16, 185, 129), width=3, radius=30)
        draw.text((540, 1580), "Testează gratuit pe: https://lex-civic.vercel.app/", font=self.fonts["cta_url"], fill=(52, 211, 153), anchor="mm")
        draw.text((540, 1635), "Simulator Clauze Abuzive • Calculatoare Civice • Modele Cereri", font=self.fonts["footer_bold"], fill=(229, 231, 235), anchor="mm")
        draw.text((540, 1680), "Link accesibil în Bio!", font=self.fonts["body_bold"], fill=(251, 191, 36), anchor="mm")

        # Disclaimer Legal & Operator conform CAEN 8559
        draw.text((540, 1775), "Operator: TEODORESCU O. DIANA PFA • Cod CAEN 8559 (Învățământ n.c.a.)", font=self.fonts["footer_bold"], fill=(156, 163, 175), anchor="mm")
        draw.text((540, 1810), "Informații strict educative, fără caracter de consultanță avocațială (Legea 51/1995)", font=self.fonts["footer"], fill=(107, 114, 128), anchor="mm")

        # 4. BARA DE PROGRES A SCENELOR (y: 1870 - 1890)
        total_w = 920
        start_x = 80
        prog_w = int((scene_idx + 1) / total_scenes * total_w)
        draw.rounded_rectangle([start_x, 1870, start_x + total_w, 1885], radius=7, fill=(31, 41, 55))
        draw.rounded_rectangle([start_x, 1870, start_x + prog_w, 1885], radius=7, fill=(59, 130, 246))

        return img

    async def _generate_audio_file(self, text: str, output_path: str):
        """Generează fișierul audio MP3 cu Edge-TTS."""
        # Curăță textul de emoticoane și simboluri ce pot distorsiona vocea
        clean_text = text.replace("🚫", "").replace("🔑", "").replace("🛑", "").replace("⏱️", "").replace("💼", "").replace("⚖️", "")
        communicate = edge_tts.Communicate(clean_text, self.voice)
        await communicate.save(output_path)

    def _get_media_duration(self, file_path: str) -> float:
        """Extrage durata exactă a unui fișier audio/video folosind ffmpeg."""
        cmd = [self.ffmpeg_exe, "-i", file_path]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
        import re
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            hours = float(m.group(1))
            mins = float(m.group(2))
            secs = float(m.group(3))
            return hours * 3600 + mins * 60 + secs
        return 5.0 # fallback

    def generate_video_for_script(self, script_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Construiește videoclipul complet 1080x1920 MP4 pentru scriptul dat.
        Returnează calea către fișierul video generat.
        """
        script_id = script_data.get("id", "tiktok_video")
        domain = script_data.get("domain", "Educație Civică")
        scenes = script_data.get("scenes", [])

        # Dacă scriptul nu are scene structurate definite explicit, le generăm automat
        if not scenes:
            scenes = self._auto_create_scenes(script_data)

        if not output_path:
            output_path = os.path.join(VIDEOS_DIR, f"{script_id}.mp4")

        total_scenes = len(scenes)
        temp_dir = tempfile.mkdtemp(prefix="lexcivic_video_")
        part_files = []

        try:
            print(f"[*] Generare videoclip pentru: '{script_data.get('title')}' ({total_scenes} scene)...")

            for idx, sc in enumerate(scenes):
                # 1. Generează cadrul grafic PNG
                frame_img = self.render_scene_frame(sc, domain, idx, total_scenes)
                frame_png = os.path.join(temp_dir, f"frame_{idx:02d}.png")
                frame_img.save(frame_png)

                # 2. Generează narațiunea audio MP3 pentru această scenă
                spoken_text = sc.get("spoken_text", sc.get("headline", ""))
                audio_mp3 = os.path.join(temp_dir, f"audio_{idx:02d}.mp3")
                asyncio.run(self._generate_audio_file(spoken_text, audio_mp3))

                # 3. Durata audio exactă
                duration = self._get_media_duration(audio_mp3)
                # Adăugăm o mică marjă de pauză (0.3s) pentru cursivitate între scene
                scene_duration = duration + 0.3

                # 4. Randează bucata video aferentă scenei
                part_mp4 = os.path.join(temp_dir, f"part_{idx:02d}.mp4")
                part_files.append(part_mp4)

                cmd = [
                    self.ffmpeg_exe, "-y",
                    "-loop", "1",
                    "-i", frame_png,
                    "-i", audio_mp3,
                    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
                    "-c:a", "aac", "-b:a", "128k",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    part_mp4
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                print(f"    -> Scena #{idx + 1}/{total_scenes} randată ({duration:.1f}s)...", flush=True)

            # 5. Concatenează toate părțile într-un singur video MP4 final
            concat_list = os.path.join(temp_dir, "concat.txt")
            with open(concat_list, "w", encoding="utf-8") as f:
                for p in part_files:
                    escaped = p.replace("\\", "/")
                    f.write(f"file '{escaped}'\n")

            print("[*] Concatenare scene în videoclipul final...")
            cmd_concat = [
                self.ffmpeg_exe, "-y",
                "-f", "concat", "-safe", "0",
                "-i", concat_list,
                "-c", "copy",
                "-movflags", "+faststart",
                output_path
            ]
            subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"[+] Videoclip generat cu succes: {output_path} ({file_size_mb:.2f} MB)")
            return output_path

        finally:
            # Curățare fișiere temporare
            try:
                for f in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, f))
                os.rmdir(temp_dir)
            except Exception:
                pass

    def _auto_create_scenes(self, script_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback dacă scriptul nu are scene predefinite."""
        hook_spoken = script_data.get("hook_spoken", "")
        script_body = script_data.get("script_body", "")
        title = script_data.get("title", "")

        return [
            {
                "badge": "ALARMĂ JURIDICĂ",
                "badge_color": (220, 38, 38),
                "headline": title,
                "body_points": [hook_spoken],
                "spoken_text": hook_spoken,
                "citation": "Află ce prevede legislația din România!"
            },
            {
                "badge": "CE PREVEDE LEGEA",
                "badge_color": (217, 119, 6),
                "headline": "Regula Legală Esențială",
                "body_points": [p for p in script_body.split("\n\n") if p][:2],
                "spoken_text": script_body[:len(script_body)//2],
                "citation": "Conform legislației civile și penale în vigoare"
            },
            {
                "badge": "CUM TE APERI",
                "badge_color": (16, 185, 129),
                "headline": "Soluția Practică Recomandată",
                "body_points": [p for p in script_body.split("\n\n") if p][2:],
                "spoken_text": script_body[len(script_body)//2:],
                "citation": "Operator TEODORESCU O. DIANA PFA • CAEN 8559"
            }
        ]

if __name__ == "__main__":
    from automation.tiktok_content_vault import TIKTOK_SCRIPTS
    gen = TikTokVideoGenerator()
    test_script = TIKTOK_SCRIPTS[0]
    out = gen.generate_video_for_script(test_script)
    print("Test video generat la:", out)
