import json
from django.core.management.base import BaseCommand
from account.models import Province, City


class Command(BaseCommand):
    help = 'Import Province and Cities from iran_province_city.json file'

    def handle(self, *args, **options):

        with open("data/jsons/iran_province_city.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
            for province_name, cities in data.items():
                province, created = Province.objects.get_or_create(name=province_name)

                for city in cities:
                    City.objects.get_or_create(name=city, province=province)

        self.stdout.write(self.style.SUCCESS('Successfully imported locations'))
