from telethon.sync import TelegramClient, functions
from django.conf import settings
from parsing.parsers import Parser, parse_channel
from parsing.utils import MessageType
import asyncio


def get_channel(channel_id, messages_limit):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with TelegramClient(
        settings.TELEGRAM_SESSION_FILE,
        settings.TELEGRAM_APP_ID,
        settings.TELEGRAM_APP_HASH,
        loop=loop,
    ) as client:
        channel = parse_channel(
            channel_id,
            client(functions.channels.GetFullChannelRequest(channel=channel_id)),
        )
        channel.messages = __get_channel_messages(client, channel, messages_limit)
    return channel


def __get_channel_messages(client, channel, messages_limit):
    def get_messages_indexes(messages, grouped_id, type=None, inverse=False):
        type_predicate = lambda m: m != type if inverse else m == type
        indexes = []
        for i in range(len(messages)):
            message = messages[i]
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
                messages.remove(i)
        else:
            indexes = get_messages_indexes(
                messages, new_message.grouped_id, type=MessageType.TEXT
            )
            if len(indexes) == 0:
                messages.append(new_message)

    channel_messages = []
    for t_message in client.iter_messages(channel.channel_id, limit=messages_limit):
        parser = Parser.from_message(channel, t_message)
        if parser is not None:
            message = parser.parse(channel, t_message)
            if message is not None:
                if message.grouped_id is not None:
                    merge_messages(channel_messages, message)
                else:
                    channel_messages.append(message)

    return channel_messages
