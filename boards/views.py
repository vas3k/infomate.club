from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.http import last_modified

from boards.cache import board_last_modified_at
from boards.helpers import regroup_articles_by_feed
from boards.models import Board, BoardBlock, BoardFeed, Article


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
    feeds = BoardFeed.objects.select_related("block").filter(board=board)
    articles = Article.objects.select_related("feed").filter(
        board=board,
        created_at__gt=datetime.utcnow() - timedelta(days=settings.OLD_ARTICLES_CLEANUP_AFTER_DAYS)
    )
    result = render(request, "board.html", {
        "board": board,
        "blocks": blocks,
        "feeds": feeds,
        "articles_grouped_by_feed": regroup_articles_by_feed(articles),
    })
    cache.set(f"board_{board.slug}", result, settings.BOARD_CACHE_SECONDS)
    return result


@cache_page(settings.STATIC_PAGE_CACHE_SECONDS)
def what(request):
    return render(request, "what.html")


@cache_page(settings.STATIC_PAGE_CACHE_SECONDS)
def privacy_policy(request):
    return render(request, "docs/privacy_policy.html")
