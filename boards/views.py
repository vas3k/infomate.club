from django.shortcuts import render, get_object_or_404

from auth.helpers import authorized_user
from boards.models import Board, BoardBlock, BoardFeed


def index(request):
    boards = Board.objects.filter(is_visible=True).all()
    return render(request, "index.html", {
        "boards": boards
    })


def board(request, board_slug):
    board = get_object_or_404(Board, slug=board_slug)

    if board.is_private:
        me = authorized_user(request)
        if not me:
            return render(request, "board_no_access.html", {
                "board": board
            }, status=401)

    blocks = BoardBlock.objects.filter(board=board)
    feeds = BoardFeed.objects.filter(board=board)
    return render(request, "board.html", {
        "board": board,
        "blocks": blocks,
        "feeds": feeds,
    })


def what(request):
    return render(request, "what.html")


def privacy_policy(request):
    return render(request, "docs/privacy_policy.html")
