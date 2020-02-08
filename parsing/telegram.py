from telethon.sync import TelegramClient, functions
from django.conf import settings
from parsing.parsers import Parser, parse_channel
import asyncio


def get_channel(channel_id, messages_limit):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with TelegramClient(settings.TELEGRAM_SESSION_FILE, settings.TELEGRAM_APP_ID, settings.TELEGRAM_APP_HASH, loop=loop) as client:
        channel = parse_channel(channel_id, client(functions.channels.GetFullChannelRequest(channel=channel_id)))
        channel.messages = __get_channel_messages(client, channel, messages_limit)
    return channel


def __get_channel_messages(client, channel, messages_limit):
    channel_messages = []
    for t_message in client.iter_messages(channel.channel_id, limit=messages_limit):
        parser = Parser.from_message(channel, t_message)
        if parser is not None:
            message = parser.parse(channel, t_message)
            if message is not None:
                channel_messages.append(message)

    return channel_messages
