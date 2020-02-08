from django.db import models


class TelegramChannel(models.Model):
    channel_id = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=300)
    description = models.TextField()
    last_update = models.DateTimeField()


class TelegramChannelMessage(models.Model):
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=300)
    description = models.TextField()
    channel = models.ForeignKey(TelegramChannel, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

