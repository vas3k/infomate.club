from boards.models import Board


def board_last_modified_at(request, board_slug):
    return Board.objects.filter(slug=board_slug).first().refreshed_at
