import io
import os
import sys
import django
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infomate.settings")
django.setup()

import re
import logging
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
from newspaper import Article as NewspaperArticle, ArticleException

from boards.models import BoardFeed, Article, Board
from scripts.common import DEFAULT_REQUEST_HEADERS, DEFAULT_REQUEST_TIMEOUT, MAX_PARSABLE_CONTENT_LENGTH

DEFAULT_NUM_WORKER_THREADS = 5
DEFAULT_ENTRIES_LIMIT = 100
MIN_REFRESH_DELTA = timedelta(minutes=30)

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
        never_updated_feeds = BoardFeed.objects.filter(refreshed_at__isnull=True)
        if not force:
            need_to_update_feeds = BoardFeed.objects.filter(
                rss__isnull=False,
                refreshed_at__lte=datetime.utcnow() - MIN_REFRESH_DELTA
            )
        else:
            need_to_update_feeds = BoardFeed.objects.filter(rss__isnull=False)
        need_to_update_feeds = list(never_updated_feeds) + list(need_to_update_feeds)

    tasks = []
    for feed in need_to_update_feeds:
        tasks.append({
            "id": feed.id,
            "board_id": feed.board_id,
            "name": feed.name,
            "rss": feed.rss,
            "conditions": feed.conditions,
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
    feed = feedparser.parse(item['rss'])
    print(f"Entries found: {len(feed.entries)}")
    for entry in feed.entries[:DEFAULT_ENTRIES_LIMIT]:
        entry_title = parse_title(entry)
        entry_link = parse_link(entry)
        if not entry_title or not entry_link:
            print("No entry title or link. Skipped")
            continue

        print(f"- article: '{entry_title}' {entry_link}")
        
        conditions = item.get("conditions") 
        if conditions:
            is_valid = check_conditions(conditions, entry)
            if not is_valid:
                print(f"Condition {conditions} does not match. Skipped")
                continue
        
        article, is_created = Article.objects.get_or_create(
            board_id=item["board_id"],
            feed_id=item["id"],
            uniq_id=entry.get("id") or entry.get("guid") or entry_link,
            defaults=dict(
                url=entry_link[:2000],
                domain=parse_domain(entry_link)[:256],
                created_at=parse_datetime(entry),
                updated_at=datetime.utcnow(),
                title=entry_title[:256],
                image=str(parse_rss_image(entry) or "")[:512],
                description=entry.get("summary"),
            )
        )

        if is_created:
            # parse heavy info
            text, lead_image = parse_rss_text_and_image(entry)

            if text:
                article.description = text[:1000]

            if lead_image:
                article.image = lead_image[:512]

            # get real url
            real_url, content_type, content_length = resolve_url(entry_link)

            # load and summarize article
            if item["is_parsable"] and content_length <= MAX_PARSABLE_CONTENT_LENGTH \
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

    week_ago = datetime.utcnow() - timedelta(days=7)
    frequency = Article.objects.filter(feed_id=item["id"], created_at__gte=week_ago).count()
    last_article = Article.objects.filter(feed_id=item["id"]).order_by("-created_at").first()

    BoardFeed.objects.filter(id=item["id"]).update(
        refreshed_at=datetime.utcnow(),
        last_article_at=last_article.created_at if last_article else None,
        frequency=frequency or 0
    )


def check_conditions(conditions, entry):
    if not conditions:
        return True

    for condition in conditions:
        if condition["type"] == "in":
            if condition["in"] not in entry[condition["field"]]:
                return False

    return True


def resolve_url(entry_link):
    url = str(entry_link)
    content_type = None
    content_length = MAX_PARSABLE_CONTENT_LENGTH + 1  # don't parse null content-types
    depth = 10
    while depth > 0:
        depth -= 1

        try:
            response = requests.head(url, timeout=DEFAULT_REQUEST_TIMEOUT, verify=False, stream=True)
        except RequestException:
            log.warning(f"Failed to resolve URL: {url}")
            return None, content_type, content_length

        if 300 < response.status_code < 400:
            url = response.headers["location"]  # follow redirect
        else:
            content_type = response.headers.get("content-type")
            content_length = int(response.headers.get("content-length") or 0)
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


def parse_title(entry):
    title = entry.get("title") or entry.get("description") or entry.get("summary")
    return re.sub("<[^<]+?>", "", title).strip()


def parse_link(entry):
    if entry.get("link"):
        return entry["link"]

    if entry.get("links"):
        return entry["links"][0]["href"]

    return None


def parse_rss_image(entry):
    if entry.get("media_content"):
        images = [m["url"] for m in entry["media_content"] if m.get("medium") == "image" and m.get("url")]
        if images:
            return images[0]

    if entry.get("image"):
        if isinstance(entry["image"], dict):
            return entry["image"].get("href")
        return entry["image"]

    return None


def parse_rss_text_and_image(entry):
    if not entry.get("summary"):
        return "", ""

    bs = BeautifulSoup(entry["summary"], features="lxml")
    text = re.sub(r"\s\s+", " ", bs.text or "").strip()

    img_tags = bs.findAll("img")
    for img_tag in img_tags:
        src = img_tag.get("src", None)
        if src:
            return text, src

    return text, ""


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
