from django.shortcuts import render, get_object_or_404

from boards.models import Board, BoardBlock, BoardFeed, Article


def index(request):
    boards = Board.objects.filter(is_visible=True).order_by("created_at")
    return render(request, "index.html", {
        "boards": boards
    })


def board(request, board_slug):
    board = get_object_or_404(Board, slug=board_slug)
    blocks = BoardBlock.objects.filter(board=board)
    feeds = BoardFeed.objects.filter(board=board)
    return render(request, "board.html", {
        "board": board,
        "blocks": blocks,
        "feeds": feeds,
    })
