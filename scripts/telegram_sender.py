import io
import os
import sys
import django
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infomate.settings")
django.setup()

import logging
from datetime import timedelta, datetime
import threading
import queue

import click

from boards.models import Article

from notifications.telegram.common import INFOMATE_DE_CHANNEL, send_telegram_message, Chat, render_html_message

DEFAULT_NUM_WORKER_THREADS = 5
DEFAULT_ENTRIES_LIMIT = 30
MIN_REFRESH_DELTA = timedelta(minutes=30)
DELETE_OLD_ARTICLES_DELTA = timedelta(days=300)

log = logging.getLogger()


@click.command()
def send_telegram_updates():
    articles = Article.objects.select_related('feed').filter(board__slug='de').order_by('-updated_at')[:1]

    for article in articles:
        # split description on paragraphs
        paragraphs = article.description.split('\n')

        send_telegram_message(
            chat=INFOMATE_DE_CHANNEL,
            text=render_html_message(
                "article_as_post.html",
                article=article,
                paragraphs=paragraphs,
            ),
        )


if __name__ == '__main__':
    send_telegram_updates()
