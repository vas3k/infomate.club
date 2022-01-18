from uuid import uuid4

from django.db import models
from boards.models import Article


class PublishHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    article = models.ForeignKey(
        Article,
        related_name='published',
        on_delete=models.CASCADE
    )
    channel_id = models.CharField(max_length=256)
    published_at = models.DateTimeField(auto_now_add=True)

    telegram_message_id = models.IntegerField()

    class Meta:
        db_table = "publish_history"
        ordering = ["-published_at"]
