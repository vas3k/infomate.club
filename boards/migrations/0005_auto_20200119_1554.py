# Generated by Django 2.2.8 on 2020-01-19 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0004_auto_20200107_1904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='curator_title',
            field=models.CharField(max_length=120, null=True),
        ),
    ]