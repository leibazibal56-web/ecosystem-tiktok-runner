import os

# Configuration for TikTok Legal Automation & Telegram Dispatcher
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

# Telegram Bot Credentials (from ecosystem)
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "8867321650").strip()

# Gemini API Key (optional for dynamic AI generation)
GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()

# Platform URL
PLATFORM_URL = "https://lex-civic.vercel.app/"
OPERATOR_NAME = "TEODORESCU O. DIANA PFA"
CAEN_CODE = "8559 - Alte forme de învățământ n.c.a."
