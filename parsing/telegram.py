from abc import ABC, abstractmethod
from telethon.sync import TelegramClient, functions
from django.conf import settings
import asyncio
import re


class TelegramChannel:

    def __init__(self, channel_id=None, title=None, link=None, description=None, messages=None):
        self.channel_id = channel_id
        self.title = title
        self.link = link
        self.description = description
        self.messages = messages if messages is not None else []

    def add_message(self, message):
        self.messages.append(message)

    def remove_message(self, message):
        self.messages.remove(message)


class TelegramChannelMessage:

    def __init__(self, telegram_id=None, title=None, description=None, link=None, channel=None, timestamp=None):
        self.telegram_id = telegram_id
        self.title = title
        self.description = description
        self.link = link
        self.channel = channel
        self.timestamp = timestamp


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
        for parser in _parsers:
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


def get_channel(channel_id, messages_limit):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with TelegramClient(settings.TELEGRAM_SESSION_FILE, settings.TELEGRAM_APP_ID, settings.TELEGRAM_APP_HASH, loop=loop) as client:
        channel = __get_channel_info(client, channel_id)
        channel.messages = __get_channel_messages(client, channel, messages_limit)
    return channel


def __get_channel_info(client, channel_id):
    chat_full = client(functions.channels.GetFullChannelRequest(channel=channel_id))
    return TelegramChannel(
        channel_id=channel_id,
        title=chat_full.chats[0].title,
        description=chat_full.full_chat.about,
        link=_TELEGRAM_CHANNEL_LINK.format(chat_full.chats[0].username)
    )


def __get_channel_messages(client, channel, messages_limit):
    channel_messages = []
    for t_message in client.iter_messages(channel.channel_id, limit=messages_limit):
        parser = Parser.from_message(channel, t_message)
        if parser is not None:
            message = parser.parse(channel, t_message)
            if message is not None:
                channel_messages.append(message)

    return channel_messages


_TELEGRAM_CHANNEL_LINK = 'https://t.me/{}'
_TELEGRAM_MESSAGE_LINK = _TELEGRAM_CHANNEL_LINK + '/{}'

_parsers = [
    MarkdownParser(),
    SimpleTextParser()
]
