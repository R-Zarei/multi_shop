import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from product.models import Brand

class Command(BaseCommand):
    help = 'Create 38 realistic brands and link corresponding logo images'

    def handle(self, *args, **kwargs):
        source_dir = os.path.join(settings.BASE_DIR, 'data/images/brand_logos')
        os.makedirs(source_dir, exist_ok=True)

        brands_data = [
            # Initial 20 brands
            ('Adidas', 'adidas.png'), ('Bosch', 'bosch.png'),
            ('LC Waikiki', 'lc-waikiki.jpeg'), ('Loreal', 'loreal.png'),
            ('Oila', 'oila.png'), ('Philips', 'philips.png'),
            ('Sony', 'sony.png'), ('Zara', 'zara.png'),
            ('Apple', 'apple.png'), ('H&M', 'hm.png'),
            ('LG', 'lg.png'), ('Nestle', 'nestle.png'),
            ('Samsung', 'samsung.png'), ('Asus', 'asus.png'),
            ('Kalleh', 'kaleh.png'), ('Lipton', 'lipton.jpeg'),
            ('Nike', 'nike.png'), ('Panasonic', 'panasonic.png'),
            ('Snowa', 'snowa.jpg'), ('Xiaomi', 'xiaomi.png'),

            # Newly added 18 brands (Puma and Casio excluded)
            ('AMD', 'AMD.jpeg'),
            ('Braun', 'Braun.png'),
            ('Canon', 'Canon.png'),
            ('IKEA', 'IKEA.jpg'),
            ('Intel', 'Intel.jpeg'),
            ('JBL', 'JBL.png'),
            ('Kingston', 'Kingston.png'),
            ('Lego', 'Lego.png'),
            ('Logitech', 'Logitech.png'),
            ('MSI', 'MSI.png'),
            ('Makita', 'Makita.png'),
            ('Nvidia', 'Nvidia.png'),
            ('Omron', 'Omron.png'),
            ('Pampers', 'Pampers.jpeg'),
            ('Pioneer', 'Pioneer.jpeg'),
            ('Ronix', 'Ronix.png'),
            ('Tefal', 'Tefal.png'),
            ('Western Digital', 'Western_Digital.jpeg'),
        ]

        created_count = 0

        for name, filename in brands_data:
            file_path = os.path.join(source_dir, filename)

            if not Brand.objects.filter(name=name).exists():
                brand = Brand(name=name)

                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        brand.logo.save(filename, File(f), save=False)
                else:
                    self.stdout.write(self.style.WARNING(f'Logo file not found: {filename}'))

                brand.save()
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Brand "{name}" created.'))
            else:
                self.stdout.write(f'Brand "{name}" already exists.')

        self.stdout.write(self.style.SUCCESS(f'\nTotal new brands added: {created_count}'))