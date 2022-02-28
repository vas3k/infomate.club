import os
import sys
import django
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infomate.settings")
django.setup()

import logging
from datetime import timedelta, datetime
from random import random
from time import sleep

import click

from boards.models import Article
from notifications.models import PublishHistory, BoardTelegramChannel
from notifications.telegram.common import (
    send_telegram_message, Chat, render_html_message,
)

log = logging.getLogger()

DEBUG = os.getenv("DEBUG", True) in ('True', True)
TG_MESSAGES_ONE_TIME_LIMIT = 3

TEXT_LIMIT = 500


def get_article_text(article: Article):
    if article.summary:
        return article.summary.split('\n')

    elif article.description:
        return [article.description[:TEXT_LIMIT] + ' [...]']

    else:
        return None


@click.command()
@click.option("--board-slug", help="To send articles from one particular board")
@click.option("--tg_msg_limit", help="To send exact amount of articles to telegram", default=None)
def send_telegram_updates(board_slug, tg_msg_limit):
    if board_slug:
        telegram_channels = BoardTelegramChannel.objects\
            .select_related('board')\
            .filter(board__slug=board_slug)

    else:
        telegram_channels = BoardTelegramChannel.objects\
            .select_related('board').all()

    week_ago = datetime.utcnow() - timedelta(days=7)

    for channel in telegram_channels:
        channel_name = channel.telegram_channel_id

        # get only articles which were not yet published
        # to this particular channel
        articles = Article.objects\
            .select_related('feed')\
            .select_related('board')\
            .filter(board=channel.board)\
            .filter(created_at__gte=week_ago)\
            .exclude(published__channel_id=channel_name)\
            .exclude(feed__block__is_publishing_to_telegram=False)

        print(f'\nSending {len(articles)} articles to Telegram {channel_name}')
        if (DEBUG or tg_msg_limit) and articles:
            limit = tg_msg_limit or TG_MESSAGES_ONE_TIME_LIMIT
            print(f'  limit articles to {limit}')
            articles = articles[:limit]

        for article in articles:
            text = get_article_text(article)

            if article.is_fresh() or True:
                message = send_telegram_message(
                    chat=Chat(id=channel_name),
                    text=render_html_message(
                        "article_as_post.html",
                        article=article,
                        paragraphs=text,
                        tg_channel=channel_name
                    ),
                )
                print(f'\t... sent article {article.feed.name} / {article.title[:30]}[...]')
                sleep(1 + random())

                if message:
                    article_sent = PublishHistory.objects.create(
                        article=article,
                        channel_id=channel_name,
                        telegram_message_id=message.message_id,
                    )

                    article_sent.save()


if __name__ == '__main__':
    send_telegram_updates()
