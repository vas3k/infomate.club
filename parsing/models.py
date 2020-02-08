from django.db import models


class TelegramChannel(models.Model):
    channel_id = models.CharField(max_length=100)
    title = models.CharField(max_length=512)
    link = models.CharField(max_length=512)
    description = models.TextField()


class TelegramChannelMessage(models.Model):
    title = models.TextField()
    link = models.CharField(max_length=512)
    telegram_id = models.IntegerField(null=True)
    description = models.TextField()
    channel = models.ForeignKey(TelegramChannel, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

