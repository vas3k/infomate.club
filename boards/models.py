import uuid
from datetime import datetime, timedelta

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.contrib.postgres.fields import JSONField
from slugify import slugify

from boards.icons import DOMAIN_ICONS


class Board(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)

    name = models.CharField(max_length=120, db_index=True)
    avatar = models.URLField(max_length=512, null=True)

    curator_name = models.CharField(max_length=120)
    curator_title = models.CharField(max_length=120, null=True)
    curator_url = models.TextField(null=True)
    curator_bio = models.TextField(null=True)
    curator_footer = models.TextField(null=True)

    schema = models.TextField(null=True)

    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()
    refreshed_at = models.DateTimeField(null=True)

    is_visible = models.BooleanField(default=True)
    is_private = models.BooleanField(default=True)
    index = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "boards"
        ordering = ["index", "name"]

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()

        if not self.slug:
            self.slug = slugify(self.name).lower()

        self.updated_at = datetime.utcnow()

        return super().save(*args, **kwargs)

    def board_name(self):
        return self.name or self.curator_name

    def natural_refreshed_at(self):
        if not self.refreshed_at:
            return "now..."
        return naturaltime(self.refreshed_at)


class BoardBlock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, related_name="blocks", on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=512, null=True)
    slug = models.SlugField()

    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()

    index = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "board_blocks"
        ordering = ["index"]

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()

        if not self.slug:
            self.slug = slugify(self.name).lower()

        self.updated_at = datetime.utcnow()

        return super().save(*args, **kwargs)


class BoardFeed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, related_name="feeds", on_delete=models.CASCADE, db_index=True)
    block = models.ForeignKey(BoardBlock, related_name="feeds", on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=512, null=True)
    comment = models.TextField(null=True)
    url = models.URLField(max_length=512)
    icon = models.URLField(max_length=512, null=True)
    rss = models.URLField(max_length=512, null=True)

    created_at = models.DateTimeField(db_index=True)
    last_article_at = models.DateTimeField(null=True)
    refreshed_at = models.DateTimeField(null=True)

    frequency = models.FloatField(default=0.0)  # per week
    columns = models.SmallIntegerField(default=1)
    articles_per_column = models.SmallIntegerField(default=15)
    index = models.PositiveIntegerField(default=0)

    conditions = JSONField(null=True)
    is_parsable = models.BooleanField(default=True)

    class Meta:
        db_table = "board_feeds"
        ordering = ["index"]

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def last_articles(self):
        return self.articles.all()[:15 * self.columns]

    def articles_by_column(self):
        articles = self.articles.all()[:self.articles_per_column * self.columns]
        return [
            (column, articles[column * self.articles_per_column:self.articles_per_column * (column + 1)])
            for column in range(self.columns)
        ]

    def natural_last_article_at(self):
        if not self.last_article_at:
            return None
        return naturaltime(self.last_article_at)


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uniq_id = models.TextField(db_index=True)
    board = models.ForeignKey(Board, related_name="articles", on_delete=models.CASCADE, db_index=True)
    feed = models.ForeignKey(BoardFeed, related_name="articles", on_delete=models.CASCADE, db_index=True)
    url = models.URLField(max_length=2048)
    type = models.CharField(max_length=16)
    domain = models.CharField(max_length=256, null=True)
    title = models.CharField(max_length=256)
    image = models.URLField(max_length=512, null=True)
    description = models.TextField(null=True)
    summary = models.TextField(null=True)

    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "articles"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def icon(self):
        article_icon = DOMAIN_ICONS.get(self.domain)
        if not article_icon:
            return ""

        if article_icon.startswith("fa:"):
            return f"""<i class="{article_icon[3:]}"></i> """

        return f"""<img src="{article_icon}" alt="{self.domain}" class="icon"> """

    def natural_created_at(self):
        if not self.created_at:
            return None
        return naturaltime(self.created_at)

    def is_fresh(self):
        frequency = self.feed.frequency
        now = datetime.utcnow()

        if frequency <= 1:
            # low frequency feed — any post this week is new
            return self.created_at > now - timedelta(days=7)
        elif frequency <= 20:
            # average frequency — mark today posts
            return self.created_at > now - timedelta(days=1)
        elif frequency >= 100:
            # extra high frequency — mark newest posts
            return self.created_at > now - timedelta(hours=4)

        # normal frequency
        return self.created_at > now - timedelta(hours=8)
