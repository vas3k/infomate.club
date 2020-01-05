from django.urls import path

from auth.views import login, logout, club_callback
from boards.views import index, board, privacy_policy

urlpatterns = [
    path("", index, name="index"),

    path("docs/privacy_policy/", privacy_policy, name="privacy_policy"),

    path("auth/login/", login, name="login"),
    path("auth/club_callback/", club_callback, name="club_callback"),
    path("auth/logout/", logout, name="logout"),

    path("<slug:board_slug>/", board, name="board"),
]
