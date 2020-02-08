from abc import ABC, abstractmethod
from telethon.sync import TelegramClient, functions
from parsing.models import TelegramChannel, TelegramChannelMessage
from django.conf import settings
import asyncio
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
        channel.save()
        __update_channel_messages(client, channel, messages_limit)
    return channel


def __get_channel_info(client, channel_id):
    chat_full = client(functions.channels.GetFullChannelRequest(channel=channel_id))
    channel_db = TelegramChannel.objects.filter(channel_id=channel_id).first()

    if channel_db is None:
        channel_db = TelegramChannel(channel_id=channel_id)

    if channel_db.title != chat_full.chats[0].title or channel_db.description != chat_full.full_chat.about:
        channel_db.title = chat_full.chats[0].title
        channel_db.description = chat_full.full_chat.about
        channel_db.link = _TELEGRAM_CHANNEL_LINK.format(chat_full.chats[0].username)

    return channel_db


def __update_channel_messages(client, channel, messages_limit):
    def get_messages():
        return client.iter_messages(channel.channel_id, limit=messages_limit)

    def get_messages_to_date():
        return client.iter_messages(channel.channel_id, reverse=True, offset_date=last_message.timestamp, limit=messages_limit)

    def save_message(t_message):
        parser = Parser.from_message(channel, t_message)
        if parser is not None:
            message = parser.parse(channel, t_message)
            if message is not None:
                message.save()
                return message
        return None

    def load_last_new_message(messages_iterator):
        try:
            t_message = next(messages_iterator)
            exists_message = TelegramChannelMessage.objects.filter(channel=channel, telegram_id=t_message.id).first()
            if exists_message is None:
                return save_message(t_message)
        except StopIteration:
            pass
        return None

    def load_and_save_new_messages(message_iterator):
        for message in messages_iterator:
            save_message(message)

    last_message = TelegramChannelMessage.objects.filter(channel=channel).order_by("-timestamp").first()

    if last_message is not None:
        messages = get_messages_to_date
    else:
        messages = get_messages

    messages_iterator = messages()
    message = load_last_new_message(messages_iterator)

    if message is not None:
        load_and_save_new_messages(messages_iterator)


_TELEGRAM_CHANNEL_LINK = 'https://t.me/{}'
_TELEGRAM_MESSAGE_LINK = _TELEGRAM_CHANNEL_LINK + '/{}'

_parsers = [
    MarkdownParser(),
    SimpleTextParser()
]
