import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from product.models import Category


class Command(BaseCommand):
    help = 'Import exact categories tree from a JSON file'

    def handle(self, *args, **kwargs):
        json_file_path = os.path.join(settings.BASE_DIR, 'data/jsons', 'categories.json')

        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'File not found at: {json_file_path}'))
            return

        with open(json_file_path, 'r', encoding='utf-8') as f:
            dataset_categories = json.load(f)

        self.stdout.write(self.style.WARNING('Clearing old categories...'))
        Category.objects.update(parent=None)
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'Importing {len(dataset_categories)} categories from JSON...'))

        for cat_code in dataset_categories:
            parts = cat_code.split('.')
            parent_obj = None

            for part in parts:
                title_clean = part.replace('_', ' ').title()

                cat_obj, created = Category.objects.get_or_create(
                    name=title_clean,
                    parent=parent_obj,
                )
                parent_obj = cat_obj

        total_cats = Category.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully imported and built {total_cats} category nodes!'))