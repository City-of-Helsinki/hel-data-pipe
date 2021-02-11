# Generated by Django 3.1.3 on 2021-02-09 20:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SensorType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=100, verbose_name="Name"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "parser",
                    models.CharField(blank=True, max_length=100, verbose_name="Parser"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Device",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("devid", models.CharField(db_index=True, max_length=40, unique=True)),
                (
                    "name",
                    models.CharField(blank=True, max_length=100, verbose_name="Name"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "lat",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Latitude (dd.ddddd)"
                    ),
                ),
                (
                    "lon",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Longitude (dd.ddddd)"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "sensortype",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="SensorType",
                        to="parser.sensortype",
                    ),
                ),
            ],
        ),
    ]
