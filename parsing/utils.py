from enum import Enum


class TelegramChannel:
    def __init__(
        self, channel_id=None, title=None, link=None, description=None, messages=None
    ):
        self.channel_id = channel_id
        self.title = title
        self.link = link
        self.description = description
        self.messages = messages if messages is not None else []

    def add_message(self, message):
        self.messages.append(message)

    def remove_message(self, message):
        self.messages.remove(message)

    def to_dict(self):
        return {
            "channel_id": self.channel_id,
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "messages": list(map(lambda message: message.to_dict(), self.messages)),
        }


class TelegramChannelMessage:
    def __init__(
        self,
        telegram_id=None,
        title=None,
        description=None,
        link=None,
        channel=None,
        grouped_id=None,
        type=None,
        timestamp=None,
    ):
        self.telegram_id = telegram_id
        self.title = title
        self.description = description
        self.link = link
        self.channel = channel
        self.grouped_id = grouped_id
        self.type = type
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "telegram_id": self.telegram_id,
            "title": self.title,
            "description": self.description,
            "link": self.link,
            "channel": self.channel.channel_id,
            "grouped_id": self.grouped_id,
            "type": self.type.value,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class MessageType(Enum):
    TEXT = "text"
    VIDEO = "video"
    PHOTO = "photo"
    VOICE = "voice"
    FILE = "file"
