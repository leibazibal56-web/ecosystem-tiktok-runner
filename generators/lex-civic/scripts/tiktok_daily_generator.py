# -*- coding: utf-8 -*-
"""
LexCivic - Standard TikTok Daily Generator Entrypoint
Delegates to automation/run_daily_tiktok.py to generate the 9:16 vertical MP4 video
with Romanian neural voiceover and dispatch it to Telegram.
"""
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from automation.run_daily_tiktok import main

if __name__ == "__main__":
    main()
