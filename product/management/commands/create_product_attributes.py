from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from product.models import Color, Size, Discount


class Command(BaseCommand):
    help = 'Create base attributes: Colors, Sizes, and Discounts'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting base attributes generation...'))

        # 1. Create Colors
        color_names = [
            'Black', 'White', 'Silver', 'Space Gray', 'Gold',
            'Red', 'Blue', 'Navy', 'Green', 'Pink', 'Brown', 'Yellow'
        ]
        colors_created = 0
        for name in color_names:
            _, created = Color.objects.get_or_create(name=name)
            if created:
                colors_created += 1
        self.stdout.write(self.style.SUCCESS(f'Verified/Created {len(color_names)} Colors.'))

        # 2. Create Sizes
        size_titles = [
            # Clothing
            'XS', 'S', 'M', 'L', 'XL', 'XXL',
            # Shoes
            '38', '39', '40', '41', '42', '43', '44', '45',
            # Tech / Storage
            '64GB', '128GB', '256GB', '512GB', '1TB'
        ]
        sizes_created = 0
        for title in size_titles:
            _, created = Size.objects.get_or_create(title=title)
            if created:
                sizes_created += 1
        self.stdout.write(self.style.SUCCESS(f'Verified/Created {len(size_titles)} Sizes.'))

        # 3. Create Discounts
        today = timezone.localdate()
        discounts_data = [
            {'title': 'Summer Sale', 'percentage': 15, 'start_date': today - timedelta(days=10),
             'end_date': today + timedelta(days=20)},
            {'title': 'Black Friday', 'percentage': 30, 'start_date': today - timedelta(days=2),
             'end_date': today + timedelta(days=5)},
            {'title': 'Clearance', 'percentage': 50, 'start_date': today - timedelta(days=30),
             'end_date': today + timedelta(days=15)},
            {'title': 'Expired Sale', 'percentage': 20, 'start_date': today - timedelta(days=40),
             'end_date': today - timedelta(days=10)},
        ]

        for data in discounts_data:
            Discount.objects.get_or_create(
                title=data['title'],
                defaults={
                    'percentage': data['percentage'],
                    'start_date': data['start_date'],
                    'end_date': data['end_date']
                }
            )
        self.stdout.write(self.style.SUCCESS('Verified/Created Discounts.'))
        self.stdout.write(self.style.SUCCESS('Base attributes generation complete.'))