# config.py — .env fayldan o'qiydi

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
MAX_ELON_PER_USER = int(os.getenv("MAX_ELON_PER_USER", 5))
MAX_PHOTO_COUNT = int(os.getenv("MAX_PHOTO_COUNT", 5))
PAGE_SIZE = int(os.getenv("PAGE_SIZE", 5))
DB_FILE = os.getenv("DB_FILE", "uylar.db")
