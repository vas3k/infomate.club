import os
import logging

import telegram
from django.conf import settings

log = logging.getLogger()

TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN or os.environ.get('TELEGRAM_TOKEN')

bot = telegram.Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None
