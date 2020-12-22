import re
from collections import namedtuple
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from scripts.common import DEFAULT_REQUEST_TIMEOUT, DEFAULT_REQUEST_HEADERS

TELEGRAM_CHANNEL_WEBVIEW_PREFIX = "https://t.me/s/"
BACKGROUND_IMAGE_RE = re.compile("url\('(https://.+?)'\)")

TELEGRAM_MESSAGE_CLASS = ".tgme_widget_message"
TELEGRAM_MESSAGE_TEXT_CLASS = ".tgme_widget_message_text"
TELEGRAM_MESSAGE_PHOTO_CLASS = ".tgme_widget_message_photo_wrap"
TELEGRAM_MESSAGE_DATE_CLASS = ".tgme_widget_message_date"

TelegramChannel = namedtuple("TelegramChannel", ["url", "name", "messages"])
TelegramMessage = namedtuple("TelegramMessage", ["url", "text", "photo", "created_at"])


def parse_channel(channel_name, only_text=False, limit=100) -> TelegramChannel:
    channel_url = TELEGRAM_CHANNEL_WEBVIEW_PREFIX + channel_name
    response = requests.get(
        url=channel_url,
        timeout=DEFAULT_REQUEST_TIMEOUT,
        headers=DEFAULT_REQUEST_HEADERS,
    )

    bs = BeautifulSoup(response.text, features="lxml")

    messages = []
    message_tags = bs.select(TELEGRAM_MESSAGE_CLASS)
    for message_tag in message_tags:
        message_text = None
        message_text_tag = message_tag.select(TELEGRAM_MESSAGE_TEXT_CLASS)
        if message_text_tag:
            message_text = str(message_text_tag[0])

        message_photo = None
        message_photo_tag = message_tag.select(TELEGRAM_MESSAGE_PHOTO_CLASS)
        if message_photo_tag:
            message_photo = BACKGROUND_IMAGE_RE.search(str(message_photo_tag[0])).group(1)

        message_url = None
        message_time = datetime.utcnow()
        message_date_tag = message_tag.select(TELEGRAM_MESSAGE_DATE_CLASS)
        if message_date_tag:
            message_url = message_date_tag[0]["href"]
            message_datetime_tag = message_date_tag[0].select("time")
            if message_datetime_tag:
                message_time = datetime.strptime(message_datetime_tag[0]["datetime"][:19], "%Y-%m-%dT%H:%M:%S")

        messages.append(
            TelegramMessage(
                url=message_url,
                text=message_text,
                photo=message_photo,
                created_at=message_time,
            )
        )

    if only_text:
        messages = [m for m in messages if m.text]

    return TelegramChannel(
        url=channel_url,
        name=channel_name,
        messages=list(reversed(messages))[:limit],
    )
