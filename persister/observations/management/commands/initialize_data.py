from django.core.management.base import BaseCommand

from observations.models import Datasourcetype


class Command(BaseCommand):
    def handle(self, *args, **options):
        Datasourcetype.objects.get_or_create(
            name="Digital Matter Sensornode LoRaWAN",
            defaults={
                "description": "Digital Matter Sensornode LoRaWAN",
                "parser": "sensornode",
            },
        )
