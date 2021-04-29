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

import requests
import click
import feedparser
from requests import RequestException
from newspaper import Article as NewspaperArticle, ArticleException

from boards.models import BoardFeed, Article, Board
from scripts.filters import FILTERS
from scripts.common import DEFAULT_REQUEST_HEADERS, DEFAULT_REQUEST_TIMEOUT, MAX_PARSABLE_CONTENT_LENGTH, resolve_url, \
    parse_domain, parse_datetime, parse_title, parse_link, parse_rss_image, parse_rss_text_and_image

DEFAULT_NUM_WORKER_THREADS = 5
DEFAULT_ENTRIES_LIMIT = 30
MIN_REFRESH_DELTA = timedelta(minutes=30)
DELETE_OLD_ARTICLES_DELTA = timedelta(days=300)

log = logging.getLogger()
queue = queue.Queue()


@click.command()
@click.option("--num-workers", default=DEFAULT_NUM_WORKER_THREADS, help="Number of parser threads")
@click.option("--force", is_flag=True, help="Force to update all existing feeds")
@click.option("--feed", help="To update one particular feed")
def update(num_workers, force, feed):
    if feed:
        need_to_update_feeds = BoardFeed.objects.filter(rss=feed)
    else:
        new_feeds = BoardFeed.objects.filter(refreshed_at__isnull=True)
        outdated_feeds = BoardFeed.objects.filter(url__isnull=False)
        if not force:
            outdated_feeds = BoardFeed.objects.filter(
                refreshed_at__lte=datetime.utcnow() - MIN_REFRESH_DELTA
            )
        need_to_update_feeds = list(new_feeds) + list(outdated_feeds)

    tasks = []
    for feed in need_to_update_feeds:
        tasks.append({
            "id": feed.id,
            "board_id": feed.board_id,
            "name": feed.name,
            "rss": feed.rss,
            "mix": feed.mix,
            "conditions": feed.conditions,
            "filters": feed.filters,
            "is_parsable": feed.is_parsable,
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
    updated_boards = {feed.board_id for feed in need_to_update_feeds}
    Board.objects.filter(id__in=updated_boards).update(refreshed_at=datetime.utcnow())

    # remove old data
    Article.objects.filter(created_at__lte=datetime.now() - DELETE_OLD_ARTICLES_DELTA).delete()

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
        except Exception:
            # catch all to avoid infinite wait in .join()
            log.exception("Error refreshing feed")

        queue.task_done()


def refresh_feed(item):
    print(f"Updating feed {item['name']}...")
    if item["mix"]:
        print(f"Found a mix. Parsing one by one")
        for rss in item["mix"]:
            fetch_rss(item, rss)
    else:
        fetch_rss(item, item["rss"])

    print(f"Updating parse dates for {item['name']}")
    week_ago = datetime.utcnow() - timedelta(days=7)
    frequency = Article.objects.filter(feed_id=item["id"], created_at__gte=week_ago).count()
    last_article = Article.objects.filter(feed_id=item["id"]).order_by("-created_at").first()

    BoardFeed.objects.filter(id=item["id"]).update(
        refreshed_at=datetime.utcnow(),
        last_article_at=last_article.created_at if last_article else None,
        frequency=frequency or 0
    )


def fetch_rss(item, rss):
    print(f"Parsing RSS: {rss}")

    feed = feedparser.parse(rss)

    print(f"Entries found: {len(feed.entries)}")
    for entry in feed.entries[:DEFAULT_ENTRIES_LIMIT]:
        entry_title = parse_title(entry)
        entry_link = parse_link(entry)
        if not entry_title or not entry_link:
            print("No entry title or link. Skipped")
            continue

        print(f"- article: '{entry_title}' {entry_link}")

        # check conditions (skip articles if false)
        conditions = item.get("conditions")
        if conditions:
            is_valid = check_conditions(conditions, entry)
            if not is_valid:
                print(f"- condition {conditions} does not match. Skipped")
                continue

        # apply filters (cleanup titles, etc)
        filters = item.get("filters")
        if filters:
            for filter_code in filters:
                print(f"- applying filter {filter_code}")
                if FILTERS.get(filter_code):
                    entry = FILTERS[filter_code](entry)

        created_at = parse_datetime(entry)
        if created_at <= datetime.utcnow() - DELETE_OLD_ARTICLES_DELTA:
            print(f"- article is too old. Skipped")
            continue

        entry_title = parse_title(entry)
        entry_link = parse_link(entry)
        article, is_created = Article.objects.get_or_create(
            board_id=item["board_id"],
            feed_id=item["id"],
            uniq_id=entry.get("id") or entry.get("guid") or entry_link,
            defaults=dict(
                url=entry_link[:2000],
                domain=parse_domain(entry_link)[:256],
                created_at=created_at,
                updated_at=datetime.utcnow(),
                title=entry_title[:256],
                image=str(parse_rss_image(entry) or "")[:512],
                description=entry.get("summary"),
            )
        )

        if is_created:
            print(f"- article is new, parsing metadata...")

            # parse heavy info
            text, lead_image = parse_rss_text_and_image(entry)

            if text:
                article.description = text[:1000]

            if lead_image:
                article.image = lead_image[:512]

            # get real url
            real_url, content_type, content_length = resolve_url(entry_link)

            # load and summarize article
            if item["is_parsable"] \
                    and content_length <= MAX_PARSABLE_CONTENT_LENGTH \
                    and content_type \
                    and content_type.startswith("text/"):  # to not try to parse podcasts :D

                if real_url:
                    article.url = real_url[:2000]
                    article.domain = parse_domain(real_url)[:256]

                try:
                    summary, summary_image = load_and_parse_full_article_text_and_image(article.url)
                except ArticleException:
                    summary = None
                    summary_image = None

                if summary:
                    article.summary = summary

                if summary_image:
                    article.image = summary_image[:512]

            article.save()


def check_conditions(conditions, entry):
    if not conditions:
        return True

    for condition in conditions:
        if condition["type"] == "in":
            if condition["word"] not in entry[condition["field"]]:
                return False

        if condition["type"] == "not_in":
            if condition["word"] in entry[condition["field"]]:
                return False

    return True


def load_page_safe(url):
    try:
        response = requests.get(
            url=url,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            headers=DEFAULT_REQUEST_HEADERS,
            stream=True  # the most important part — stream response to prevent loading everything into memory
        )
    except RequestException as ex:
        log.warning(f"Error parsing the page: {url} {ex}")
        return ""

    html = io.StringIO()
    total_bytes = 0

    for chunk in response.iter_content(chunk_size=100 * 1024, decode_unicode=True):
        total_bytes += len(chunk)
        if total_bytes >= MAX_PARSABLE_CONTENT_LENGTH:
            return ""  # reject too big pages
        html.write(chunk)

    return html.getvalue()


def load_and_parse_full_article_text_and_image(url):
    article = NewspaperArticle(url)
    article.set_html(load_page_safe(url))  # safer than article.download()
    article.parse()
    article.nlp()
    return article.summary, article.top_image


if __name__ == '__main__':
    update()
