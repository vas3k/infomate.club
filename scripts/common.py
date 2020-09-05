import logging
import re
import socket
from datetime import datetime
from time import mktime
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from requests import RequestException
from urllib3.exceptions import InsecureRequestWarning

import requests

log = logging.getLogger(__name__)

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 "
                  "Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}
DEFAULT_REQUEST_TIMEOUT = 10
MAX_PARSABLE_CONTENT_LENGTH = 15 * 1024 * 1024  # 15Mb

socket.setdefaulttimeout(DEFAULT_REQUEST_TIMEOUT)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


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