from abc import ABC, abstractmethod

from parsing.telegram.cleanup import cleanup_telegram_message_text
from parsing.telegram.models import TelegramChannelMessage, TelegramChannel, MessageType


class Parser(ABC):
    def parse(self, channel, message):
        return TelegramChannelMessage(
            channel=channel,
            link=_TELEGRAM_MESSAGE_LINK.format(channel.channel_id, message.id),
            telegram_id=message.id,
            grouped_id=message.grouped_id,
            timestamp=message.date,
        )

    @abstractmethod
    def matches(self, channel, message):
        pass

    @staticmethod
    def from_message(channel, message):
        for parser in _messages_parsers:
            if parser.matches(channel, message):
                return parser
        return None


class SimpleTextParser(Parser):
    def parse(self, channel, message):
        parsed_message = super().parse(channel, message)
        parsed_message.text = message.text
        parsed_message.clean_text = cleanup_telegram_message_text(message.text)
        parsed_message.title = self.parse_message_title(parsed_message.clean_text)
        parsed_message.type = MessageType.TEXT
        return parsed_message

    @classmethod
    def parse_message_title(cls, text):
        if text:
            return text.split("\n", 1)[0]
        return ""

    def matches(self, channel, message):
        return message.text is not None and len(message.text) > 0


class VideoParser(Parser):
    def parse(self, channel, message):
        parsed_message = super().parse(channel, message)
        parsed_message.title = "[video]"
        parsed_message.type = MessageType.VIDEO
        return parsed_message

    def matches(self, channel, message):
        return message.video is not None


class PhotoParser(Parser):
    def parse(self, channel, message):
        parsed_message = super().parse(channel, message)
        parsed_message.title = "[photo]"
        parsed_message.type = MessageType.PHOTO
        return parsed_message

    def matches(self, channel, message):
        return message.photo is not None


class FileParser(Parser):
    def parse(self, channel, message):
        parsed_message = super().parse(channel, message)
        parsed_message.title = "[file]"
        parsed_message.type = MessageType.FILE
        return parsed_message

    def matches(self, channel, message):
        return message.file is not None


class VoiceParser(Parser):
    def parse(self, channel, message):
        parsed_message = super().parse(channel, message)
        parsed_message.title = "[voice]"
        parsed_message.type = MessageType.VOICE
        return parsed_message

    def matches(self, channel, message):
        return message.voice is not None


def parse_channel(channel_id, chat_full):
    return TelegramChannel(
        channel_id=channel_id,
        title=chat_full.chats[0].title,
        description=chat_full.full_chat.about,
        link=_TELEGRAM_CHANNEL_LINK.format(chat_full.chats[0].username),
    )


_messages_parsers = [
    SimpleTextParser(),
    VideoParser(),
    PhotoParser(),
    VoiceParser(),
    FileParser(),
]

_TELEGRAM_CHANNEL_LINK = "https://t.me/{}"
_TELEGRAM_MESSAGE_LINK = _TELEGRAM_CHANNEL_LINK + "/{}"
