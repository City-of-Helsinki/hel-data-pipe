# Generated by Django 3.1.3 on 2020-11-23 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("observations", "0003_rename_unit_to_channel"),
    ]

    operations = [
        migrations.AlterField(
            model_name="channel",
            name="name",
            field=models.CharField(
                blank=True, max_length=64, null=True, verbose_name="Name"
            ),
        ),
    ]