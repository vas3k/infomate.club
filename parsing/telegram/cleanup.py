import re


def cleanup_telegram_message_text(text):
    text = str(text)
    cleanup_expressions = [
        r"\[.*?\]\(.*?\)",  # attached files and images
        r"#[\S]*",  # hashtags
        r"[\*\~\`]+",  # stars and tildas
        r"<[^>]*>",  # html tags
        r"[\n]{3,}",  # triple newlines
    ]
    for pattern in cleanup_expressions:
        text = re.sub(pattern, "", text, flags=re.M)

    return text.strip()
