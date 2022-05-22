from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.http import last_modified

from boards.cache import board_last_modified_at
from boards.models import Board, BoardBlock, BoardFeed


@cache_page(settings.STATIC_PAGE_CACHE_SECONDS)
def index(request):
    boards = Board.objects.filter(is_visible=True).all()
    return render(request, "index.html", {
        "boards": boards
    })


@last_modified(board_last_modified_at)
def board(request, board_slug):
    board = get_object_or_404(Board, slug=board_slug)

    cached_page = cache.get(f"board_{board.slug}")
    if cached_page and board.refreshed_at and board.refreshed_at <= \
            datetime.utcnow() - timedelta(seconds=settings.BOARD_CACHE_SECONDS):
        return cached_page

    blocks = BoardBlock.objects.filter(board=board)
    feeds = BoardFeed.objects.select_related("articles").filter(board=board)
    result = render(request, "board.html", {
        "board": board,
        "blocks": blocks,
        "feeds": feeds,
    })
    cache.set(f"board_{board.slug}", result, settings.BOARD_CACHE_SECONDS)
    return result


@cache_page(settings.STATIC_PAGE_CACHE_SECONDS)
def what(request):
    return render(request, "what.html")


@cache_page(settings.STATIC_PAGE_CACHE_SECONDS)
def privacy_policy(request):
    return render(request, "docs/privacy_policy.html")
