# Generated by Django 3.1.3 on 2021-02-16 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parser", "0007_auto_20210216_1255"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rawmessage",
            name="json_data",
            field=models.JSONField(
                blank=True, default="", verbose_name="Raw text converted data"
            ),
        ),
    ]
