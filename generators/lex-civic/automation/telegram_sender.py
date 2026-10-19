# -*- coding: utf-8 -*-
import json
import os
import requests
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional
from automation.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, PLATFORM_URL

class TelegramTikTokDispatcher:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID

    @property
    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id and ":" in self.token)

    def _escape_html(self, text: str) -> str:
        """Escaparea caracterelor rezervate HTML pentru Telegram API."""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def send_tiktok_video(self, video_path: str, script_data: Dict[str, Any], day_number: Optional[int] = None) -> bool:
        """
        Încarcă și trimite fișierul video MP4 (1080x1920) direct pe Telegram.
        Descrierea pentru TikTok este inclusă în blocul <code>...</code> al descrierii videoclipului,
        permițând copierea cu un singur tap/clic pe mobil și desktop.
        """
        if not self.is_configured:
            print("[Telegram] Eroare: Tokenul de bot sau Chat ID-ul nu este configurat.")
            return False

        if not os.path.exists(video_path):
            print(f"[Telegram] Eroare: Fișierul video nu există: {video_path}")
            return False

        title = script_data.get("title", "Videoclip TikTok LexCivic")
        caption = script_data.get("copyable_caption", "")
        day_tag = f"ZIUA #{day_number}" if day_number else "EDUTIKTOK"

        video_caption_html = (
            f"🎬 <b>VIDEOCLIP TIKTOK GATA DE POSTARE — {day_tag}</b>\n"
            f"📌 <b>{self._escape_html(title)}</b>\n\n"
            f"📋 <b>DESCRIERE TIKTOK (Apasă pe casetă pentru COPYPASTE 1-CLICK):</b>\n"
            f"<code>{self._escape_html(caption)}</code>\n\n"
            f"ℹ️ <i>Operator: TEODORESCU O. DIANA PFA • Cod CAEN 8559</i>"
        )

        params = {
            "chat_id": self.chat_id,
            "caption": video_caption_html,
            "parse_mode": "HTML",
            "supports_streaming": "true",
            "width": 1080,
            "height": 1920
        }

        url = f"https://api.telegram.org/bot{self.token}/sendVideo?{urllib.parse.urlencode(params)}"

        try:
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            print(f"[*] Se încarcă videoclipul pe Telegram ({file_size_mb:.2f} MB)...", flush=True)

            with open(video_path, "rb") as vf:
                resp = requests.post(
                    url,
                    files={"video": (os.path.basename(video_path), vf, "video/mp4")},
                    timeout=180
                )
                res_data = resp.json()

                if res_data.get("ok"):
                    print(f"[Telegram] Videoclipul TikTok a fost expediat cu succes către chat {self.chat_id}!", flush=True)
                    return True
                else:
                    print(f"[Telegram] Răspuns de eroare de la Telegram sendVideo: {res_data}", flush=True)
                    return False
        except Exception as e:
            print(f"[Telegram] Eroare la expedierea videoclipului pe Telegram: {e}", flush=True)
            return False

    def send_tiktok_brief(self, script_data: Dict[str, Any], day_number: Optional[int] = None) -> bool:
        """
        Trimite un brief text complet de TikTok pe Telegram cu butoane interactive.
        """
        if not self.is_configured:
            print("[Telegram] Eroare: Tokenul de bot sau Chat ID-ul nu este configurat.")
            return False

        title = script_data.get("title", "Scenariu TikTok Didactic")
        domain = script_data.get("domain", "Educație Juridică")
        hook_visual = script_data.get("hook_visual", "")
        hook_spoken = script_data.get("hook_spoken", "")
        visual_direction = script_data.get("visual_direction", "")
        script_body = script_data.get("script_body", "")
        copyable_caption = script_data.get("copyable_caption", "")

        day_tag = f"ZIUA #{day_number}" if day_number else "EDUTIKTOK"

        # Construcția mesajului HTML structurat
        message_html = (
            f"🎬 <b>LEXCIVIC TIKTOK COPILOT — {day_tag}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>Subiect:</b> {self._escape_html(title)}\n"
            f"📚 <b>Domeniu:</b> {self._escape_html(domain)}\n\n"

            f"⚡ <b>1. CÂRLIG VIZUAL (Primele 3 secunde):</b>\n"
            f"<i>{self._escape_html(hook_visual)}</i>\n\n"

            f"🗣️ <b>2. CÂRLIG VORBIT (Ce spui prima dată):</b>\n"
            f"<b>„{self._escape_html(hook_spoken)}”</b>\n\n"

            f"🎥 <b>3. INDICAȚII DE PRODUCȚIE / CADRU:</b>\n"
            f"{self._escape_html(visual_direction)}\n\n"

            f"📜 <b>4. TEXT INTEGRAL NARAȚIUNE (35–50 secunde):</b>\n"
            f"<i>{self._escape_html(script_body)}</i>\n\n"

            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 <b>DESCRIERE TIKTOK &amp; HASHTAGS (Apasă pe casetă pentru COPYPASTE 1-CLICK):</b>\n"
            f"<code>{self._escape_html(copyable_caption)}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ℹ️ <i>Operator: TEODORESCU O. DIANA PFA (Cod CAEN 8559 - Învățământ n.c.a.)</i>"
        )

        # Butoane interactive Inline Keyboard
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🌐 Deschide Platforma LexCivic", "url": PLATFORM_URL}
                ],
                [
                    {"text": "📑 Simulator Clauze Abuzive", "url": f"{PLATFORM_URL.rstrip('/')}/#tab-clauses"},
                    {"text": "💳 Calculator Popriri Salariu", "url": f"{PLATFORM_URL.rstrip('/')}/#tab-garnishment"}
                ]
            ]
        }

        payload = {
            "chat_id": self.chat_id,
            "text": message_html,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": keyboard
        }

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("ok"):
                    print(f"[Telegram] Brieful TikTok trimis cu succes către chat {self.chat_id}!", flush=True)
                    return True
                else:
                    print(f"[Telegram] Răspuns negativ de la Telegram: {data}", flush=True)
                    return False
        except Exception as e:
            print(f"[Telegram] Eroare la expedierea pe Telegram: {e}", flush=True)
            return False

    def dispatch_full_package(self, script_data: Dict[str, Any], day_number: Optional[int] = None, video_path: Optional[str] = None) -> bool:
        """
        Trimite pachetul complet:
        1. Videoclipul MP4 1080x1920 gata de postat cu descrierea 1-click copy-paste.
        2. Brieful de regie cu butoane directe către platformă.
        """
        video_success = False
        if video_path and os.path.exists(video_path):
            video_success = self.send_tiktok_video(video_path, script_data, day_number=day_number)
        
        brief_success = self.send_tiktok_brief(script_data, day_number=day_number)
        return video_success or brief_success
