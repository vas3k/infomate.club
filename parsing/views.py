from django.contrib.syndication.views import Feed

from parsing.telegram.parser import parse_channel


class TelegramChannelFeed(Feed):
    FEED_ITEMS = 30

    def get_object(self, request, channel_name):
        limit = int(request.GET.get("size") or self.FEED_ITEMS)
        only = str(request.GET.get("only") or "")
        return parse_channel(channel_name, only_text=only == "text", limit=limit)

    def title(self, obj):
        return obj.name

    def items(self, obj):
        return obj.messages

    def link(self, obj):
        return obj.url

    def item_title(self, item):
        return item.text

    def item_description(self, item):
        result = ""
        if item.photo:
            result += f"<img src=\"{item.photo}\"><br>"
        if item.text:
            result += str(item.text)
        return result

    def item_link(self, item):
        return item.url

    def item_pubdate(self, item):
        return item.created_at
