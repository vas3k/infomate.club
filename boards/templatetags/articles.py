from django import template

register = template.Library()


@register.simple_tag()
def articles_by_column(articles_grouped_by_feed, feed):
    articles = articles_grouped_by_feed[feed.id][0:feed.articles_per_column * feed.columns]
    return [
        (column, articles[column * feed.articles_per_column:feed.articles_per_column * (column + 1)])
        for column in range(feed.columns)
    ]
