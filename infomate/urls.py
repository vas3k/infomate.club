from django.conf import settings
from django.urls import path, include
from django.views.decorators.cache import cache_page

from boards.views import index, board, privacy_policy, what
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

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
}