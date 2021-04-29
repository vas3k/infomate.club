def echomsk_title_fix(entry):
    title = entry.get("title")
    if len(title) > 20 and title[17] == ":":
        entry["title"] = title[19:]
        print("NEW TITLE", entry["title"])
    return entry


FILTERS = {
    "echomsk_title_fix": echomsk_title_fix,
}
