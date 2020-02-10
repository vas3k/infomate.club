from django.urls import path

from auth.views import login, logout, club_callback
from boards.views import index, board, privacy_policy, what, export
from parsing.views import TelegramChannelFeed

urlpatterns = [
    path("", index, name="index"),
    path("what/", what, name="what"),

    path("docs/privacy_policy/", privacy_policy, name="privacy_policy"),

    path("auth/login/", login, name="login"),
    path("auth/club_callback/", club_callback, name="club_callback"),
    path("auth/logout/", logout, name="logout"),

    path("<slug:board_slug>/", board, name="board"),
    path("<slug:board_slug>/export/", export, name="export"),
    path("parsing/telegram/<str:channel>/", TelegramChannelFeed(), name="telegram_channel_feed")
]
