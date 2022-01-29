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

from infomate import settings
from boards.models import Article
from notifications.models import PublishHistory, BoardTelegramChannel
from notifications.telegram.common import (
    send_telegram_message, Chat, render_html_message,
)

log = logging.getLogger()

DEBUG = os.getenv("DEBUG", True) in ('True', True)


def get_article_text(article: Article):
    # split description on paragraphs
    text = article.summary or article.description
    if '\n' in text:
        # looks like summary
        text = text.split('\n')
    else:
        text = text[:300] + ' [...]'

    return text if isinstance(text, list) else [text]


@click.command()
def send_telegram_updates():
    telegram_channels = BoardTelegramChannel.objects.select_related('board').all()

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
        if DEBUG and articles:
            print('  DEBUG>> limit articles to 3')
            articles = articles[:3]

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
