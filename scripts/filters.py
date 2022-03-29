import re


def echomsk_title_fix(entry):
    title = entry.get("title")
    if len(title) > 20 and title[17] == ":":
        entry["title"] = title[19:]
    return entry


def moscow_python_podcast_clean_title(entry):
    title = entry.get("title")
    entry["title"] = title.lstrip('Moscow Python Podcast.')
    return entry


def databrew_podcast_clean_title(entry):
    title = entry.get("title")
    entry["title"] = title.replace('Data Brew ', '').replace(' Episode ', 'E')
    return entry


def remove_hashtags(entry):
    title = entry.get("title")
    entry["title"] = re.sub("#[A-Za-z0-9_]+", "", title)
    return entry


FILTERS = {
    "echomsk_title_fix": echomsk_title_fix,
    "moscow_python_podcast_clean_title": moscow_python_podcast_clean_title,
    "databrew_podcast_clean_title": databrew_podcast_clean_title,
    "remove_hashtags": remove_hashtags,
}
