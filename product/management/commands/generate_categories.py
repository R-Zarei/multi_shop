import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from product.models import Category


class Command(BaseCommand):
    help = 'Import exact categories tree from a JSON file and attach images'

    def handle(self, *args, **kwargs):
        json_file_path = os.path.join(settings.BASE_DIR, 'data', 'jsons', 'categories.json')
        images_dir = os.path.join(settings.BASE_DIR, 'data', 'images', 'categories_img')

        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'File not found at: {json_file_path}'))
            return

        with open(json_file_path, 'r', encoding='utf-8') as f:
            dataset_categories = json.load(f)

        self.stdout.write(self.style.WARNING('Clearing old categories...'))
        Category.objects.update(parent=None)
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'Importing {len(dataset_categories)} categories from JSON...'))

        # 1. Build the category tree
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

        # 2. Attach images to categorize
        if not os.path.exists(images_dir):
            self.stdout.write(self.style.ERROR(f'Images directory not found: {images_dir}'))
            return

        self.stdout.write(self.style.WARNING('Attaching images to categories...'))
        available_files = os.listdir(images_dir)
        matched_count = 0

        for category in Category.objects.all():
            matched_file = None

            # Get the full path (e.g., Computers > Peripherals > Camera)
            full_path = category.get_full_path()

            # Generate possible file names (single name or full path)
            candidates = [
                f"{category.name}.jpeg",
                f"{category.name}.jpg",
                f"{category.name.replace(' ', '_')}.jpeg",
                f"{category.name.replace(' ', 'ـ')}.jpeg",  # Handle special dash character from the list
                f"{full_path.replace(' > ', '_')}.jpeg",
                f"{full_path.replace(' > ', 'ـ')}.jpeg",
            ]

            # Find the first matching image in the directory
            for cand in candidates:
                if cand in available_files:
                    matched_file = cand
                    break

            # Save the image to the category model
            if matched_file:
                file_path = os.path.join(images_dir, matched_file)
                with open(file_path, 'rb') as f:
                    category.image.save(matched_file, File(f), save=True)
                matched_count += 1
                self.stdout.write(f' - Attached: {matched_file} -> {category.name}')

        self.stdout.write(
            self.style.SUCCESS(f'\nFinished! Successfully attached images to {matched_count} categories.'))