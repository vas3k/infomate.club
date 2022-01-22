from uuid import uuid4
from datetime import datetime

from django.db import models

from boards.models import Article, Board


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


class BoardTelegramChannel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    board = models.ForeignKey(
        Board,
        related_name='telegram_channel',
        on_delete=models.CASCADE
    )
    telegram_channel_id = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()

    class Meta:
        verbose_name = 'telegram channel to publish Board\'s updates'
        db_table = "board_telegram_channel"
        ordering = ["-updated_at"]
        constraints = [models.UniqueConstraint(
            fields=('board', 'telegram_channel_id'),
            name='unique_board_telegram_channel',
        )]

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
