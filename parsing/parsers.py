from abc import ABC, abstractmethod
from parsing.utils import TelegramChannelMessage, TelegramChannel
import re


class Parser(ABC):

    def parse(self, channel, message):
        return TelegramChannelMessage(channel=channel,
                                      link=_TELEGRAM_MESSAGE_LINK.format(channel.channel_id, message.id),
                                      telegram_id=message.id,
                                      timestamp=message.date)

    @abstractmethod
    def matches(self, channel, message):
        pass

    @staticmethod
    def from_message(channel, message):
        for parser in _messages_parsers:
            if parser.matches(channel, message):
                return parser
        return None


class MarkdownParser(Parser):
    TITLE = "\*.+\*"
    DESCRIPTION = ""

    def parse(self, channel, message):
        parsed_message = super().parse(channel, message)
        matches = re.match(self.TITLE, message.text)

        if matches is not None:
            parsed_message.title = matches.group(0)
        else:
            parsed_message.title = message.text

        parsed_message.description = parsed_message.title

        return parsed_message

    def matches(self, channel, message):
        return message.text is not None and re.match(self.TITLE, message.text) is not None


class SimpleTextParser(Parser):
    LINE = "^.+$"

    def parse(self, channel, message):
        parsed_message = super().parse(channel, message)
        matches = re.match(self.LINE, message.text)

        if matches is not None:
            parsed_message.title = matches.group(0)
        else:
            parsed_message.title = message.text

        parsed_message.description = parsed_message.title

        return parsed_message

    def matches(self, channel, message):
        return message.text is not None and len(message.text) > 0


def parse_channel(channel_id, chat_full):
    return TelegramChannel(
        channel_id=channel_id,
        title=chat_full.chats[0].title,
        description=chat_full.full_chat.about,
        link=_TELEGRAM_CHANNEL_LINK.format(chat_full.chats[0].username)
    )


_messages_parsers = [
    MarkdownParser(),
    SimpleTextParser()
]

_TELEGRAM_CHANNEL_LINK = 'https://t.me/{}'
_TELEGRAM_MESSAGE_LINK = _TELEGRAM_CHANNEL_LINK + '/{}'
