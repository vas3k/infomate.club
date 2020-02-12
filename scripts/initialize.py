import os
import sys
import django
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infomate.settings")
django.setup()

from urllib.parse import urljoin

import click
import requests
import yaml
import feedparser
from bs4 import BeautifulSoup

from boards.models import Board, BoardFeed, BoardBlock
from utils.images import upload_image_from_url
from scripts.common import DEFAULT_REQUEST_HEADERS


@click.command()
@click.option("--config", default="boards.yml", help="Boards YAML file")
@click.option("--board-slug", default=None, help="Board slug to parse only one exact board")
@click.option("--upload-favicons/--no-upload-favicons", default=False, help="Upload favicons")
@click.option("-y", "always_yes", is_flag=True, help="Don't ask any questions (good for scripts)")
def initialize(config, board_slug, upload_favicons, always_yes):
    yaml_file = os.path.join(BASE_DIR, config)
    with open(yaml_file) as f:
        try:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
        except yaml.YAMLError as ex:
            print(f"Bad YAML file '{yaml_file}': {ex}")
            exit(1)

    if not always_yes:
        input(f"Initializing feeds from {yaml_file}. Press Enter to continue...")

    for board_index, board_config in enumerate(config.get("boards") or []):
        if board_slug and board_config["slug"] != board_slug:
            continue

        board_name = board_config.get("name") or board_config["slug"]
        print(f"Creating board: {board_name}...")
        board, is_created = Board.objects.get_or_create(
            slug=board_config["slug"],
            defaults=dict(
                name=board_name,
                avatar=board_config["curator"].get("avatar"),
                curator_name=board_config["curator"].get("name"),
                curator_title=board_config["curator"].get("title"),
                curator_footer=board_config["curator"].get("footer"),
                curator_bio=board_config["curator"].get("bio"),
                curator_url=board_config["curator"].get("url"),
                is_private=board_config.get("is_private"),
                is_visible=board_config.get("is_visible"),
                index=board_index,
            )
        )
        if not is_created:
            # update existing values
            board.name = board_config.get("name") or board_config["slug"]
            board.avatar = board_config["curator"].get("avatar")
            board.curator_name = board_config["curator"].get("name")
            board.curator_title = board_config["curator"].get("title")
            board.curator_footer = board_config["curator"].get("footer")
            board.curator_bio = board_config["curator"].get("bio")
            board.curator_url = board_config["curator"].get("url")
            board.is_private = board_config.get("is_private")
            board.is_visible = board_config.get("is_visible")
            board.index = board_index
            board.save()

        for block_index, block_config in enumerate(board_config.get("blocks") or []):
            block_name = block_config.get("name") or ""
            print(f"\nCreating block: {block_name}...")
            block, is_created = BoardBlock.objects.get_or_create(
                board=board,
                slug=block_config["slug"],
                defaults=dict(
                    name=block_name,
                    index=block_index
                )
            )

            if not is_created:
                block.index = block_index
                block.name = block_name
                block.save()

            if not block_config.get("feeds"):
                continue

            for feed_index, feed_config in enumerate(block_config.get("feeds") or []):
                feed_name = feed_config.get("name")
                feed_url = feed_config["url"]
                
                print(f"Creating or updating feed: {feed_name}...")

                feed, is_created = BoardFeed.objects.get_or_create(
                    board=board,
                    block=block,
                    url=feed_config["url"],
                    defaults=dict(
                        rss=feed_config.get("rss"),
                        name=feed_name,
                        comment=feed_config.get("comment"),
                        icon=feed_config.get("icon"),
                        index=feed_index,
                        columns=feed_config.get("columns") or 1,
                        conditions=feed_config.get("conditions"),
                        is_parsable=feed_config.get("is_parsable", True)
                    )
                )

                if not is_created:
                    feed.rss = feed_config.get("rss")
                    feed.name = feed_name
                    feed.comment = feed_config.get("comment")
                    feed.index = feed_index
                    feed.columns = feed_config.get("columns") or 1
                    feed.conditions = feed_config.get("conditions")
                    feed.is_parsable = feed_config.get("is_parsable", True)

                html = None

                if not feed.rss:
                    html = html or load_page_html(feed_url)
                    rss_url = feed_config.get("rss")
                    if not rss_url:
                        rss_url = find_rss_feed(feed_url, html)
                        if not rss_url:
                            print(f"RSS feed for '{feed_name}' not found. "
                                  f"Please specify 'rss' key.")
                            exit(1)
                        print(f"- found RSS: {rss_url}")

                    feed.rss = rss_url

                if not feed.icon:
                    html = html or load_page_html(feed_url)
                    icon = feed_config.get("icon")
                    if not icon:
                        icon = find_favicon(feed_url, html)
                        print(f"- found favicon: {icon}")

                        if upload_favicons:
                            icon = upload_image_from_url(icon)
                            print(f"- uploaded favicon: {icon}")

                    feed.icon = icon

                feed.save()

            # delete unused feeds
            BoardFeed.objects.filter(
                board=board,
                block=block
            ).exclude(
                url__in={feed["url"] for feed in block_config.get("feeds") or []}
            ).delete()

        # delete unused blocks
        BoardBlock.objects.filter(
            board=board,
        ).exclude(
            slug__in={block["slug"] for block in board_config.get("blocks") or []}
        ).delete()

    print("Done ✅")


def load_page_html(url):
    return requests.get(
        url=url,
        headers=DEFAULT_REQUEST_HEADERS,
        allow_redirects=True,
        timeout=30,
        verify=False
    ).text


def find_rss_feed(url, html):
    bs = BeautifulSoup(html, features="lxml")
    possible_feeds = set()

    feed_urls = bs.findAll("link", rel="alternate")
    for feed_url in feed_urls:
        t = feed_url.get("type", None)
        if t:
            if "rss" in t or "xml" in t:
                href = feed_url.get("href", None)
                if href:
                    possible_feeds.add(urljoin(url, href))

    a_tags = bs.findAll("a")
    for a in a_tags:
        href = a.get("href", None)
        if href:
            if "xml" in href or "rss" in href or "feed" in href:
                possible_feeds.add(urljoin(url, href))

    for feed_url in possible_feeds:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            return feed_url

    return None


def find_favicon(url, html):
    bs = BeautifulSoup(html, features="lxml")
    link_tags = bs.findAll("link")
    for link_tag in link_tags:
        rel = link_tag.get("rel", None)
        if rel and "icon" in rel:
            href = link_tag.get("href", None)
            if href:
                return urljoin(url, href)

    return None


if __name__ == '__main__':
    initialize()
