import uuid

from django.db import models


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=1024, unique=True)
    user_id = models.IntegerField()  # original id of a club user (we don't store profiles)
    user_name = models.CharField(max_length=32, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "sessions"
