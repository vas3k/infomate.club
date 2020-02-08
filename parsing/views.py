from django.contrib.syndication.views import Feed
from parsing.models import TelegramChannel, TelegramChannelMessage


class TelegramChannelFeed(Feed):

    FEED_ITEMS = 30

    def get_object(self, request, channel):
        return TelegramChannel.objects.get(channel_id=channel)

    def title(self, obj):
        return obj.title

    def link(self, obj):
        return obj.link

    def description(self, obj):
        return obj.description

    def items(self, obj):
        return TelegramChannelMessage.objects.filter(channel=obj).order_by("-timestamp")[:self.FEED_ITEMS]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.link
