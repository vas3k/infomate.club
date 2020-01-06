import os
import sys
import django
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infomate.settings")
django.setup()

import click
from datetime import datetime, timedelta

from boards.models import Article


DEFAULT_CLEANUP_DAYS = 30


@click.command()
@click.option('--older-than-days', default=DEFAULT_CLEANUP_DAYS, help="Num days to cleanup older articles")
def cleanup(older_than_days):
    Article.objects.filter(created_at__lte=datetime.utcnow() - timedelta(days=older_than_days)).delete()


if __name__ == '__main__':
    cleanup()
