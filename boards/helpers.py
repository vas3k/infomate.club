from collections import defaultdict


def regroup_articles_by_feed(articles_list):
    articles_dict = defaultdict(list)
    for article in articles_list:
        articles_dict[article.feed_id].append(article)
    return articles_dict

