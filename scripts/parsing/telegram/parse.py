from abc import ABC, abstractmethod
from telethon import TelegramClient, events, sync, functions
import datetime
import json
import re


class Chat:

    def __init__(self, name, last_update):
        self.name = name
        self.last_update = last_update

    def to_dict(self):
        return {
            'name': self.name,
        }

    def __str__(self):
        return 'Chat(name={}, last_update={})'.format(self.name, self.last_update)


class Message:

    def __init__(self, id, from_id, date, text, chat):
        self.id = id
        self.from_id = from_id
        self.date = date
        self.text = text
        self.chat = chat

    def to_dict(self):
        return {
            'id': self.id,
            'from_id': self.from_id,
            'text': self.text,
            'chat': self.chat.to_dict()
        }

    def __str__(self):
        return 'Message(id={}, from_id={}, date={}, text={}, chat={})'.format(self.id, self.from_id, self.date, self.text, self.chat)


class RssChannel:
    def __init__(self, title, link, description, items=None):
        self.title = title
        self.link = link
        self.description = description
        self.items = items if items is not None else []

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'description': self.description,
            'items': list(map(lambda item: item.to_dict(), self.items))
        }


class RssItem:

    def __init__(self, title, link, description):
        self.title = title
        self.link = link
        self.description = description

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'description': self.description
        }


class Parser(ABC):

    @abstractmethod
    def parse(self, message, chat):
        pass

    @abstractmethod
    def matches(self, message):
        pass

    def _create_link(self, message, chat):
        return 'https://t.me/' + chat.username + '/' + str(message.id)


class MarkdownParser(Parser):

    TITLE = "\*.+\*"
    DESCRIPTION = ""

    def parse(self, message, chat):
        matches = re.match(self.TITLE, message.text)
        description = None

        if matches is not None:
            title = matches.group(0)
        else:
            title = message.text

        return RssItem(title, self._create_link(message, chat), None)

    def matches(self, message):
        return re.match(self.TITLE, message.text) is not None


class SimpleTextParser(Parser):
    LINE = "^.+$"

    def parse(self, message, chat):
        matches = re.match(self.LINE, message.text)

        if matches is not None:
            title = matches.group(0)
        else:
            title = message.text

        return RssItem(title, self._create_link(message, chat), None)

    def matches(self, message):
        return True


api_id = None
api_hash = None

client = TelegramClient('channels', api_id, api_hash)


channels = [
    Chat('denissexy', datetime.date(2020, 2, 6))
]

parsers = [
    MarkdownParser(),
    SimpleTextParser()
]


async def parse(message, chat):
    for parser in parsers:
        if parser.matches(message):
            return parser.parse(message, chat)
    return None


async def generate_rss(chat):
    chat_full = await client(functions.channels.GetFullChannelRequest(channel=chat.name))
    rss = RssChannel(chat_full.chats[0].title, chat_full.chats[0].username, chat_full.full_chat.about)
    async for message in client.iter_messages(chat.name, limit=2):
        rss_item = await parse(message, chat_full.chats[0])
        if rss_item is not None:
            rss.items.append(rss_item)
    return rss


async def main():
    for channel in channels:
        rss = await generate_rss(channel)
        print(json.dumps(rss.to_dict(), indent=2))



with client:
    client.loop.run_until_complete(main())
