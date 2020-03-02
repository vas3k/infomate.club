from telethon.sync import TelegramClient, functions
from django.conf import settings

from parsing.exceptions import ParsingException
from parsing.telegram.parsers import Parser, parse_channel
from parsing.telegram.models import MessageType
import asyncio

DEFAULT_LIMIT = 30


def get_channel(channel_id, *, types=None, limit=DEFAULT_LIMIT):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with TelegramClient(
        settings.TELEGRAM_SESSION_FILE,
        settings.TELEGRAM_APP_ID,
        settings.TELEGRAM_APP_HASH,
        loop=loop,
    ) as client:
        try:
            channel = parse_channel(
                channel_id,
                client(functions.channels.GetFullChannelRequest(channel=channel_id)),
            )
        except ValueError:
            raise ParsingException(f"No channel named '{channel_id}'")

        channel.messages = get_channel_messages(client, channel, types=types, limit=limit)

    return channel


def get_channel_messages(client, channel, *, types=None, limit=DEFAULT_LIMIT):
    def get_messages_indexes(messages, grouped_id, type=None, inverse=False):
        type_predicate = lambda m: m != type if inverse else m == type
        indexes = []
        for i, message in enumerate(messages):
            if type_predicate(message) and message.grouped_id == grouped_id:
                indexes.append(i)
        return indexes

    def merge_messages(messages, new_message):
        if new_message.type == MessageType.TEXT:
            indexes = get_messages_indexes(
                messages, new_message.grouped_id, type=MessageType.TEXT, inverse=True
            )
            if len(indexes) > 0:
                messages[indexes.pop()] = new_message

            for i in indexes:
                try:
                    messages.remove(i)
                except ValueError:
                    pass  # skip missing messages
        else:
            indexes = get_messages_indexes(
                messages, new_message.grouped_id, type=MessageType.TEXT
            )
            if len(indexes) == 0:
                messages.append(new_message)

    channel_messages = []

    for t_message in client.iter_messages(channel.channel_id, limit=limit):
        parser = Parser.from_message(channel, t_message)
        if parser is not None:
            message = parser.parse(channel, t_message)
            if message is not None:
                if types and message.type not in types:
                    continue

                if message.grouped_id is not None:
                    merge_messages(channel_messages, message)
                else:
                    channel_messages.append(message)

    return channel_messages
