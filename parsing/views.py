from django.contrib.syndication.views import Feed
from django.http import Http404

from parsing.exceptions import ParsingException
from parsing.telegram.telegram import get_channel


class TelegramChannelFeed(Feed):

    FEED_ITEMS = 30

    def get_object(self, request, channel):
        limit = int(request.GET["size"]) if "size" in request.GET else self.FEED_ITEMS

        try:
            return get_channel(channel, limit)
        except ParsingException:
            raise Http404()

    def title(self, obj):
        return obj.title

    def link(self, obj):
        return obj.link

    def description(self, obj):
        return obj.description

    def items(self, obj):
        return obj.messages

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.clean_text

    def item_link(self, item):
        return item.link
