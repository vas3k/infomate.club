import os
import sys
import django
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infomate.settings")
django.setup()

import re
import logging
import socket
from datetime import timedelta, datetime
from urllib.parse import urlparse

from time import mktime
import threading
import queue

import requests
import click
import feedparser
from bs4 import BeautifulSoup
from requests import RequestException
from newspaper import Article as NewspaperArticle

from boards.models import BoardFeed, Article, Board

DEFAULT_NUM_WORKER_THREADS = 5
DEFAULT_ENTRIES_LIMIT = 100
MIN_REFRESH_DELTA = timedelta(minutes=30)
REQUEST_TIMEOUT = 10
MAX_PARSABLE_CONTENT_LENGTH = 5 * 1024 * 1024  # 5Mb

log = logging.getLogger()
queue = queue.Queue()

socket.setdefaulttimeout(REQUEST_TIMEOUT)


@click.command()
@click.option("--num-workers", default=DEFAULT_NUM_WORKER_THREADS, help="Number of parser threads")
@click.option("--force", is_flag=True, help="Force to update all existing feeds")
@click.option("--feed", help="To update one particular feed")
def update(num_workers, force, feed):
    if feed:
        need_to_update_feeds = BoardFeed.objects.filter(rss=feed)
        never_updated_feeds = []
    else:
        never_updated_feeds = BoardFeed.objects.filter(refreshed_at__isnull=True)
        if not force:
            need_to_update_feeds = BoardFeed.objects.filter(
                rss__isnull=False,
                refreshed_at__lte=datetime.utcnow() - MIN_REFRESH_DELTA
            )
        else:
            need_to_update_feeds = BoardFeed.objects.filter(rss__isnull=False)

    tasks = []
    for feed in list(never_updated_feeds) + list(need_to_update_feeds):
        tasks.append({
            "id": feed.id,
            "board_id": feed.board_id,
            "name": feed.name,
            "rss": feed.rss
        })

    threads = []
    for i in range(num_workers):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    # put tasks to the queue
    for item in tasks:
        queue.put(item)

    # wait until tasks are done
    queue.join()

    # update timestamps
    Board.objects.all().update(refreshed_at=datetime.utcnow())

    # stop workers
    for i in range(num_workers):
        queue.put(None)

    for t in threads:
        t.join()


def worker():
    while True:
        task = queue.get()
        if task is None:
            break

        try:
            refresh_feed(task)
        except Exception as ex:
            log.exception("Error refreshing feed")
            pass  # to avoid infinite wait in .join()

        queue.task_done()


def refresh_feed(item):
    print(f"Updating feed {item['name']}...")
    feed = feedparser.parse(item['rss'])
    for entry in feed.entries[:DEFAULT_ENTRIES_LIMIT]:
        entry_title = entry.get("title") or entry.get("description") or entry.get("summary")
        print(f"- article: '{entry_title}' {entry.link}")
        article, is_created = Article.objects.get_or_create(
            board_id=item["board_id"],
            feed_id=item["id"],
            uniq_id=entry.get("id") or entry.get("guid") or entry.link,
            defaults=dict(
                url=entry.link[:2000],
                domain=parse_domain(entry.link)[:256],
                created_at=parse_datetime(entry),
                updated_at=datetime.utcnow(),
                title=entry.title[:256]
            )
        )

        if is_created:
            # parse heavy info
            real_url, content_type, content_length = resolve_url(entry)

            if content_length <= MAX_PARSABLE_CONTENT_LENGTH \
                    and content_type.startswith("text/"):  # to not try to parse podcasts :D

                if real_url:
                    article.url = real_url[:2000]
                    article.domain = parse_domain(real_url)[:256]

                text, lead_image = parse_rss_entry(entry)

                if text:
                    article.description = text[:1000]

                if lead_image:
                    article.image = lead_image[:512]

                summary, summary_image = load_and_parse_full_article_text_and_image(article.url)

                article.summary = summary

                if summary_image:
                    article.image = summary_image[:512]

                article.save()

    week_ago = datetime.utcnow() - timedelta(days=7)
    frequency = Article.objects.filter(feed_id=item["id"], created_at__gte=week_ago).count()
    last_article = Article.objects.filter(feed_id=item["id"]).order_by("-created_at").first()

    BoardFeed.objects.filter(id=item["id"]).update(
        refreshed_at=datetime.utcnow(),
        last_article_at=last_article.created_at if last_article else None,
        frequency=frequency or 0
    )


def resolve_url(entry):
    url = entry.link
    content_type = None
    content_length = None
    depth = 10
    while depth > 0:
        depth -= 1

        try:
            response = requests.head(url, timeout=REQUEST_TIMEOUT)
        except RequestException:
            log.warning(f"Failed to resolve URL: {entry.link}")
            return None, content_type, content_length

        if 300 < response.status_code < 400:
            url = response.headers["location"]
        else:
            content_type = response.headers.get("content-type")
            content_length = response.headers.get("content-length")
            break

    return url, content_type, content_length


def parse_domain(url):
    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def parse_datetime(entry):
    published_time = entry.get("published_parsed") or entry.get("updated_parsed")
    if published_time:
        return datetime.fromtimestamp(mktime(published_time))
    return datetime.utcnow()


def parse_rss_entry(entry):
    bs = BeautifulSoup(entry.summary, features="lxml")
    text = re.sub(r"\s\s+", " ", bs.text or "").strip()

    img_tags = bs.findAll("img")
    for img_tag in img_tags:
        src = img_tag.get("src", None)
        if src:
            return text, src

    return text, ""


def load_and_parse_full_article_text_and_image(url):
    article = NewspaperArticle(url)
    article.download()
    article.parse()
    article.nlp()
    return article.summary, article.top_image


if __name__ == '__main__':
    update()
