

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

