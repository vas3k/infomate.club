# Generated by Django 2.2.13 on 2022-01-18 03:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_auto_20220118_0344'),
    ]

    operations = [
        migrations.RenameField(
            model_name='boardtelegramchannel',
            old_name='channel_id',
            new_name='telegram_channel_id',
        ),
    ]
