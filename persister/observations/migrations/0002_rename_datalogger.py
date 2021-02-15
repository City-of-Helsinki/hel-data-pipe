# Generated by Django 3.1.3 on 2020-11-19 14:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("observations", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="channel",
            old_name="datalogger",
            new_name="datasource",
        ),
        migrations.RemoveField(
            model_name="datasource",
            name="datalogger",
        ),
        migrations.AddField(
            model_name="datasource",
            name="datasourcetype",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="datasources",
                to="observations.datasourcetype",
            ),
        ),
    ]
