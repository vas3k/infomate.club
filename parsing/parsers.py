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


class SimpleTextParser(Parser):
    MARKDOWN_BOLD = ".+\*.+\*.+"
    SIMPLE_TEXT_POST = "(.+)\n+(.+)"

    def parse(self, channel, message):
        parsed_message = super().parse(channel, message)
        (title, description) = self.parse_text(message)
        parsed_message.title = self.enhance_title(title)
        parsed_message.description = description
        return parsed_message

    def parse_text(self, message):
        matcher = re.match(self.SIMPLE_TEXT_POST, message.text)
        if matcher is not None:
            if len(matcher.groups()) > 1:
                title = matcher.group(1)
                description = matcher.group(2)
            else:
                title = matcher.group(1)
                description = message.text
        else:
            title = message.text
            description = message.text
        return title, description

    def enhance_title(self, title):
        matcher = re.match(self.MARKDOWN_BOLD, title)
        return title.replace("*", "") if matcher is not None else title

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
    SimpleTextParser()
]

_TELEGRAM_CHANNEL_LINK = 'https://t.me/{}'
_TELEGRAM_MESSAGE_LINK = _TELEGRAM_CHANNEL_LINK + '/{}'
