import os
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from product.models import Category, Brand, Product, ProductImage, Color, Size, Discount, Information


# noinspection unreachable-code
class Command(BaseCommand):
    help = 'Generate mock products with strict, realistic leaf-to-brand mapping and assign attributes'

    def handle(self, *args, **kwargs):
        source_dir = os.path.join(settings.BASE_DIR, 'data/images/products')

        if not os.path.exists(source_dir):
            self.stdout.write(self.style.ERROR(f'Source directory not found: {source_dir}'))
            return

        available_files = os.listdir(source_dir)

        # Load Base Attributes from DB
        all_colors = list(Color.objects.all())
        all_discounts = list(Discount.objects.all())

        clothing_sizes = list(Size.objects.filter(title__in=['XS', 'S', 'M', 'L', 'XL', 'XXL']))
        shoe_sizes = list(Size.objects.filter(title__in=['38', '39', '40', '41', '42', '43', '44', '45']))
        tech_sizes = list(Size.objects.filter(title__in=['64GB', '128GB', '256GB', '512GB', '1TB']))

        info_texts = [
            "Premium build quality and durable materials.",
            "Includes 18 months of official warranty.",
            "Eco-friendly packaging and sustainable production.",
            "Lightweight design for everyday comfortable use.",
            "Water and dust resistant for extreme conditions.",
            "Designed and manufactured using global standard guidelines."
        ]

        if not all_colors or not clothing_sizes:
            self.stdout.write(self.style.ERROR('Base attributes missing. Run create_attributes first!'))
            return

        # Explicit brand mappings per specific leaf category
        SPECIFIC_LEAF_BRAND_MAPPING = {
            # Computer hardware & internal components
            'cpu': ['Intel', 'AMD'],
            'motherboard': ['Asus', 'MSI'],
            'videocards': ['Nvidia', 'Asus', 'MSI', 'AMD'],
            'hdd': ['Western Digital', 'Kingston'],
            'memory': ['Kingston', 'Samsung'],
            'cooler': ['Asus', 'MSI'],
            'power supply': ['Asus', 'MSI'],

            # Pre-built computers & peripherals
            'desktop': ['Asus', 'Apple', 'MSI'],
            'notebook': ['Apple', 'Asus', 'Xiaomi', 'MSI'],
            'keyboard': ['Logitech', 'Asus', 'Xiaomi'],
            'mouse': ['Logitech', 'Asus', 'Xiaomi'],
            'monitor': ['Samsung', 'LG', 'Asus', 'Xiaomi'],
            'printer': ['Canon', 'Panasonic'],
            'camera': ['Canon', 'Sony', 'Panasonic'],
            'photo': ['Canon', 'Sony'],
            'video': ['Sony', 'Panasonic', 'Canon'],

            # Audio, multimedia & musical instruments
            'headphone': ['Sony', 'Apple', 'JBL', 'Logitech', 'Xiaomi'],
            'acoustic': ['JBL', 'Pioneer', 'Sony'],
            'subwoofer': ['JBL', 'Pioneer', 'Sony'],
            'microphone': ['Sony', 'JBL', 'Logitech'],
            'piano': ['Sony'],
            'player': ['Pioneer', 'Sony'],

            # Tech Accessories, health & wearables
            'clocks': ['Apple', 'Samsung', 'Xiaomi'],
            'tonometer': ['Omron', 'Philips'],
            'scales': ['Xiaomi', 'Omron', 'Tefal'],

            # Fashion Accessories
            'umbrella': ['Zara', 'H&M', 'LC Waikiki'],
            'belt': ['Zara', 'H&M', 'LC Waikiki'],
            'sunglasses': ['Zara', 'H&M'],
            'glasses': ['Zara', 'H&M'],
            'tie': ['Zara', 'H&M'],
            'bag': ['Zara', 'H&M', 'Nike', 'Adidas'],
            'wallet': ['Zara', 'H&M'],

            # Cosmetics & Beauty
            'perfume': ['Loreal', 'Zara'],
            'makeup': ['Loreal'],
            'cosmetics': ['Loreal'],

            # Furniture, home & lighting
            'bed': ['IKEA'],
            'table': ['IKEA'],
            'cabinet': ['IKEA'],
            'chair': ['IKEA'],
            'sofa': ['IKEA'],
            'light': ['IKEA', 'Philips', 'Xiaomi'],
            'blanket': ['IKEA', 'Zara'],
            'pillow': ['IKEA', 'Zara'],

            # Kids & baby care
            'toys': ['Lego'],
            'diapers': ['Pampers'],
            'carriage': ['LC Waikiki', 'Zara'],
            'dolls': ['Lego', 'Zara'],

            # Tools & outdoor machinery
            'drill': ['Makita', 'Ronix', 'Bosch'],
            'saw': ['Makita', 'Ronix', 'Bosch'],
            'welding': ['Ronix', 'Bosch'],
            'pump': ['Makita', 'Ronix'],
            'generator': ['Ronix', 'Makita'],
            'lawn mower': ['Makita', 'Bosch'],
            'cultivator': ['Makita', 'Bosch'],

            # Kitchen & small appliances
            'blender': ['Braun', 'Philips', 'Bosch', 'Tefal'],
            'mixer': ['Braun', 'Philips', 'Bosch', 'Tefal'],
            'juicer': ['Braun', 'Philips', 'Panasonic', 'Bosch'],
            'meat grinder': ['Panasonic', 'Bosch', 'Philips'],
            'coffee machine': ['Philips', 'Bosch'],
            'coffee grinder': ['Bosch', 'Tefal'],
            'toster': ['Tefal', 'Philips', 'Bosch'],
            'grill': ['Tefal', 'Bosch', 'Philips'],
            'steam cooker': ['Tefal', 'Philips'],
            'iron': ['Philips', 'Tefal', 'Braun'],
            'hair cutter': ['Braun', 'Philips', 'Panasonic'],

            # Large household appliances
            'refrigerators': ['Samsung', 'LG', 'Bosch', 'Snowa'],
            'washer': ['LG', 'Samsung', 'Bosch', 'Snowa'],
            'dishwasher': ['Bosch', 'LG', 'Samsung'],
            'microwave': ['Samsung', 'LG', 'Panasonic'],
            'vacuum': ['Bosch', 'Philips', 'Panasonic', 'Xiaomi'],

            # Apparel & sports
            'tshirt': ['Nike', 'Adidas', 'Zara', 'H&M', 'LC Waikiki'],
            'jeans': ['Zara', 'H&M', 'LC Waikiki'],
            'jacket': ['Nike', 'Adidas', 'Zara', 'H&M'],
            'shorts': ['Nike', 'Adidas'],
            'keds': ['Nike', 'Adidas'],
            'moccasins': ['Zara', 'LC Waikiki'],
            'sandals': ['Zara', 'LC Waikiki', 'Nike', 'Adidas'],
            'tennis': ['Nike', 'Adidas'],
            'trainer': ['Nike', 'Adidas'],
            'bicycle': ['Nike', 'Adidas'],
        }

        # Fallback root mapping
        ROOT_FALLBACK_BRAND_MAPPING = {
            'apparel': ['Nike', 'Adidas', 'Zara', 'H&M', 'LC Waikiki'],
            'sport': ['Nike', 'Adidas'],
            'accessories': ['Zara', 'H&M', 'LC Waikiki', 'Loreal'],
            'appliances': ['LG', 'Bosch', 'Philips', 'Panasonic', 'Snowa', 'Samsung', 'Tefal', 'Braun'],
            'electronics': ['Apple', 'Samsung', 'Sony', 'Xiaomi', 'LG', 'Panasonic', 'Asus', 'JBL', 'Pioneer'],
            'computers': ['Apple', 'Asus', 'Xiaomi', 'MSI', 'Kingston', 'Logitech', 'Western Digital'],
            'kids': ['Lego', 'Pampers', 'LC Waikiki', 'Zara', 'H&M', 'Nestle'],
            'auto': ['Bosch', 'Philips', 'Panasonic', 'Pioneer'],
            'construction': ['Bosch', 'Makita', 'Ronix'],
            'medicine': ['Omron', 'Philips', 'Braun'],
            'country yard': ['Bosch', 'Makita', 'Ronix'],
            'furniture': ['IKEA', 'Zara', 'H&M'],
            'stationery': ['Xiaomi', 'IKEA', 'Lego'],
            'grocery': ['Kalleh', 'Lipton', 'Oila', 'Nestle'],
            'default': ['IKEA', 'Zara', 'Philips', 'Xiaomi']
        }

        # Product generation count weights for primary categories
        CATEGORY_PRODUCT_WEIGHTS = {
            'smartphone': 12, 'notebook': 10, 'headphone': 10, 'clocks': 10,
            'tv': 8, 'tshirt': 8, 'jeans': 8, 'shoes': 8, 'keds': 8,
            'desktop': 8, 'tablet': 8, 'vacuum': 6, 'microwave': 6,
        }
        DEFAULT_PRODUCT_COUNT = 5

        leaf_categories = Category.objects.filter(children__isnull=True)
        all_brands = {b.name: b for b in Brand.objects.all()}

        if not leaf_categories.exists() or not all_brands:
            self.stdout.write(self.style.ERROR('Categories or brands missing in database.'))
            return

        self.stdout.write(self.style.WARNING('Clearing existing products, images, and info records...'))
        Product.objects.all().delete()
        Information.objects.all().delete()

        total_products = 0

        for category in leaf_categories:
            # 1. Match local category image
            matched_file = None
            full_path_clean = category.get_full_path().replace(' > ', 'ـ')
            candidates = [
                f"{full_path_clean}.jpeg", f"{full_path_clean}.jpg",
                f"{category.name.replace(' ', 'ـ')}.jpeg", f"{category.name.replace(' ', 'ـ')}.jpg",
                f"{category.name.replace(' ', '_')}.jpeg", f"{category.name.replace(' ', '_')}.jpg",
                f"{category.name}.jpeg", f"{category.name}.jpg"
            ]
            for cand in candidates:
                if cand in available_files:
                    matched_file = cand
                    break

            # 2. Extract safe names and resolve root_key for all categories
            cat_clean_name = category.name.strip().lower()

            root_cat = category
            while root_cat.parent is not None:
                root_cat = root_cat.parent
            root_key = root_cat.name.strip().lower()

            # 3. Select matching brand objects
            if cat_clean_name in SPECIFIC_LEAF_BRAND_MAPPING:
                allowed_brand_names = SPECIFIC_LEAF_BRAND_MAPPING[cat_clean_name]
            else:
                allowed_brand_names = ROOT_FALLBACK_BRAND_MAPPING.get(root_key, ROOT_FALLBACK_BRAND_MAPPING['default'])

            matched_brand_objects = [all_brands[name] for name in allowed_brand_names if name in all_brands]
            if not matched_brand_objects:
                matched_brand_objects = list(all_brands.values())

            # 4. Create products and attach images & attributes
            num_products = CATEGORY_PRODUCT_WEIGHTS.get(cat_clean_name, DEFAULT_PRODUCT_COUNT)

            for _ in range(num_products):
                chosen_brand = random.choice(matched_brand_objects)
                price = Decimal(random.randint(150, 45000) * 1000)
                model_number = random.randint(100, 999)

                # Determine Discount (25% chance of getting a discount)
                chosen_discount = random.choice(all_discounts) if all_discounts and random.random() < 0.25 else None

                product = Product.objects.create(
                    title=f'{chosen_brand.name} {category.name} Pro {model_number}',
                    brand=chosen_brand,
                    category=category,
                    price=price,
                    discount=chosen_discount,
                    description=f'Original {category.name} manufactured by {chosen_brand.name}. High durability and standard quality.'
                )

                # Handle Product Image
                if matched_file:
                    src_file_path = os.path.join(source_dir, matched_file)
                    with open(src_file_path, 'rb') as f:
                        img_obj = ProductImage(product=product)
                        img_obj.image.save(matched_file, File(f), save=True)

                # Assign Colors (1 to 3 random colors)
                if all_colors:
                    product.color.set(random.sample(all_colors, k=random.randint(1, min(3, len(all_colors)))))

                # Assign Sizes based on Category Type
                if cat_clean_name in ['tshirt', 'jeans', 'jacket', 'shorts', 'dress', 'shirt'] or root_key == 'apparel':
                    if clothing_sizes:
                        product.size.set(
                            random.sample(clothing_sizes, k=random.randint(2, min(5, len(clothing_sizes)))))
                elif cat_clean_name in ['keds', 'moccasins', 'sandals', 'tennis', 'trainer', 'shoes']:
                    if shoe_sizes:
                        product.size.set(random.sample(shoe_sizes, k=random.randint(3, min(6, len(shoe_sizes)))))
                elif cat_clean_name in ['smartphone', 'notebook', 'tablet', 'memory', 'hdd']:
                    if tech_sizes:
                        product.size.set(random.sample(tech_sizes, k=random.randint(1, min(3, len(tech_sizes)))))

                # Create Information entries (2 to 3 points per product)
                selected_info = random.sample(info_texts, k=random.randint(2, 3))
                for text in selected_info:
                    Information.objects.create(product=product, text=text)

                total_products += 1

            self.stdout.write(
                f'Category "{category.name}" matched with brands: {[b.name for b in matched_brand_objects]}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nExecution complete: Successfully generated {total_products} products with all attributes.'))