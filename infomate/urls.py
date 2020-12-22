from django.urls import path
from django.views.decorators.cache import cache_page

from boards.views import index, board, privacy_policy, what
from infomate import settings
from parsing.views import TelegramChannelFeed

urlpatterns = [
    path("", index, name="index"),
    path("what/", what, name="what"),

    path("docs/privacy_policy/", privacy_policy, name="privacy_policy"),

    path("<slug:board_slug>/", board, name="board"),

    path("parsing/telegram/<str:channel_name>/",
         cache_page(settings.TELEGRAM_CACHE_SECONDS)(TelegramChannelFeed()),
         name="telegram_channel_feed"),

]
