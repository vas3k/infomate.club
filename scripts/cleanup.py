import os
import sys
import django
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infomate.settings")
django.setup()

import click
from datetime import datetime, timedelta

from django.conf import settings

from boards.models import Article, BoardFeed


@click.command()
@click.option(
    '--older-than-days',
    default=settings.OLD_ARTICLES_CLEANUP_AFTER_DAYS,
    help="Num days to cleanup older articles"
)
@click.option(
    '--more-than-amount',
    default=settings.OLD_ARTICLES_CLEANUP_AFTER_AMOUNT,
    help="Max amount of articles allowed in feed"
)
def cleanup(older_than_days, more_than_amount):
    click.echo(f"Cleaning up articles older than {older_than_days} days...")
    Article.objects.filter(created_at__lte=datetime.utcnow() - timedelta(days=older_than_days)).delete()
    for feed in BoardFeed.objects.all():
        click.echo(f"Cleaning up feed {feed.name}, leaving {more_than_amount} last articles...")
        last_article_to_leave = Article.objects\
            .filter(feed=feed)\
            .order_by("created_at")[more_than_amount:more_than_amount + 1].first()
        if last_article_to_leave:
            num_deleted, _ = Article.objects.filter(feed=feed, created_at__gt=last_article_to_leave.created_at).delete()
            click.echo(f"Deleted {num_deleted} old articles!")
    click.echo("Done")


if __name__ == '__main__':
    cleanup()
