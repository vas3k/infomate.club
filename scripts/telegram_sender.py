import io
import os
import sys
import django
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infomate.settings")
django.setup()

import logging
from datetime import timedelta, datetime

import click

from boards.models import Article
from notifications.models import PublishHistory

from notifications.telegram.common import INFOMATE_DE_CHANNEL, send_telegram_message, Chat, render_html_message

log = logging.getLogger()


@click.command()
def send_telegram_updates():
    tg_channel = INFOMATE_DE_CHANNEL

    # get only articles which were not yet published
    # to this particular channel
    articles = Article.objects\
        .select_related('feed')\
        .filter(board__slug='de')\
        .exclude(published__channel_id=tg_channel.id)\

    for article in articles[:1]:
        # split description on paragraphs
        paragraphs = article.description.split('\n')

        if article.is_fresh():
            message = send_telegram_message(
                chat=tg_channel,
                text=render_html_message(
                    "article_as_post.html",
                    article=article,
                    paragraphs=paragraphs,
                ),
            )

            article_sent = PublishHistory.objects.create(
                article=article,
                channel_id=tg_channel.id,
                telegram_message_id=message.message_id,
            )

            article_sent.save()


if __name__ == '__main__':
    send_telegram_updates()