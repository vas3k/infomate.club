from uuid import uuid4

from django.db import models
from boards.models import Article


class SentHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    article = models.ForeignKey(Article, related_name='sent', on_delete=models.DO_NOTHING)
    channel_id = models.CharField(max_length=256)

    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sent_history"
        ordering = ["-sent_at"]
