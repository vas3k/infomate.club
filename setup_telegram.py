import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infomate.settings")
import django
django.setup()

from telethon.sync import TelegramClient
from django.conf import settings


with TelegramClient(settings.TELEGRAM_SESSION_FILE, settings.TELEGRAM_APP_ID, settings.TELEGRAM_APP_HASH) as client:
    print("Successfully setup Telegram session.")
