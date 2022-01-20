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

from infomate import settings
from boards.models import Article
from notifications.models import PublishHistory, BoardTelegramChannel
from notifications.telegram.common import INFOMATE_DE_CHANNEL, send_telegram_message, Chat, render_html_message

log = logging.getLogger()

SEND_LIMIT = 5 if settings.DEBUG else 10000


@click.command()
def send_telegram_updates():
    # TODO: get channel from database (for each article / board?)
    # BoardTelegramChannel.objects.filter()
    tg_channel = INFOMATE_DE_CHANNEL

    # get only articles which were not yet published
    # to this particular channel
    articles = Article.objects\
        .select_related('feed')\
        .select_related('board')\
        .filter(board__slug='de')\
        .exclude(published__channel_id=tg_channel.id)\
        .exclude(feed__block__is_publishing_to_telegram=False)


    print(f'\nSending {len(articles)} articles to Telegram {tg_channel.id}')
    for article in articles[:3]:
        # split description on paragraphs
        text = article.summary or article.description
        paragraphs = text.split('\n')

        if article.is_fresh() or True:
            message = send_telegram_message(
                chat=tg_channel,
                text=render_html_message(
                    "article_as_post.html",
                    article=article,
                    paragraphs=paragraphs,
                    tg_channel=tg_channel.id if tg_channel.id[0] == '@' else '@' + tg_channel.id
                ),
            )
            print(f'\t... sent article {article.title[:20]}[...]')

            article_sent = PublishHistory.objects.create(
                article=article,
                channel_id=tg_channel.id,
                telegram_message_id=message.message_id,
            )

            article_sent.save()


if __name__ == '__main__':
    send_telegram_updates()
