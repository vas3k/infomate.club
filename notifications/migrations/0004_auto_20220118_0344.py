# Generated by Django 2.2.13 on 2022-01-18 03:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_auto_20220118_0343'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boardtelegramchannel',
            options={'ordering': ['-updated_at'], 'verbose_name': "telegram channel to publish Board's updates"},
        ),
    ]