from enum import Enum


class TelegramChannel:
    def __init__(
        self,
        channel_id=None,
        title=None,
        link=None,
        description=None,
        messages=None
    ):
        self.channel_id = channel_id
        self.title = title
        self.link = link
        self.description = description
        self.messages = messages or []


class TelegramChannelMessage:
    def __init__(
        self,
        telegram_id=None,
        title=None,
        text=None,
        clean_text=None,
        link=None,
        channel=None,
        grouped_id=None,
        type=None,
        timestamp=None,
    ):
        self.telegram_id = telegram_id
        self.title = title
        self.text = text
        self.clean_text = clean_text
        self.link = link
        self.channel = channel
        self.grouped_id = grouped_id
        self.type = type
        self.timestamp = timestamp


class MessageType(Enum):
    TEXT = "text"
    VIDEO = "video"
    PHOTO = "photo"
    VOICE = "voice"
    FILE = "file"
