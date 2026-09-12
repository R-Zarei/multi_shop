import os
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from product.models import Category, Brand, Product, ProductImage, Color, Size, Discount, Information


# noinspection unreachable-code
class Command(BaseCommand):
    help = 'Generate mock products with realistic prices, brand mapping and attributes'

    def handle(self, *args, **kwargs):
        source_dir = os.path.join(settings.BASE_DIR, 'data/images/categories_img')

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

        # ---------------------------------------------------------
        # BRAND MAPPINGS
        # ---------------------------------------------------------
        SPECIFIC_LEAF_BRAND_MAPPING = {
            'cpu': ['Intel', 'AMD'], 'motherboard': ['Asus', 'MSI'],
            'videocards': ['Nvidia', 'Asus', 'MSI', 'AMD'], 'hdd': ['Western Digital', 'Kingston'],
            'memory': ['Kingston', 'Samsung'], 'cooler': ['Asus', 'MSI'], 'power supply': ['Asus', 'MSI'],
            'desktop': ['Asus', 'Apple', 'MSI'], 'notebook': ['Apple', 'Asus', 'Xiaomi', 'MSI'],
            'keyboard': ['Logitech', 'Asus', 'Xiaomi'], 'mouse': ['Logitech', 'Asus', 'Xiaomi'],
            'monitor': ['Samsung', 'LG', 'Asus', 'Xiaomi'], 'printer': ['Canon', 'Panasonic'],
            'camera': ['Canon', 'Sony', 'Panasonic'], 'photo': ['Canon', 'Sony'],
            'video': ['Sony', 'Panasonic', 'Canon'],
            'headphone': ['Sony', 'Apple', 'JBL', 'Logitech', 'Xiaomi'], 'acoustic': ['JBL', 'Pioneer', 'Sony'],
            'subwoofer': ['JBL', 'Pioneer', 'Sony'], 'microphone': ['Sony', 'JBL', 'Logitech'],
            'piano': ['Sony'], 'player': ['Pioneer', 'Sony'],
            'clocks': ['Apple', 'Samsung', 'Xiaomi'], 'tonometer': ['Omron', 'Philips'],
            'scales': ['Xiaomi', 'Omron', 'Tefal'],
            'umbrella': ['Zara', 'H&M', 'LC Waikiki'], 'belt': ['Zara', 'H&M', 'LC Waikiki'],
            'sunglasses': ['Zara', 'H&M'], 'glasses': ['Zara', 'H&M'], 'tie': ['Zara', 'H&M'],
            'bag': ['Zara', 'H&M', 'Nike', 'Adidas'], 'wallet': ['Zara', 'H&M'],
            'perfume': ['Loreal', 'Zara'], 'makeup': ['Loreal'], 'cosmetics': ['Loreal'],
            'bed': ['IKEA'], 'table': ['IKEA'], 'cabinet': ['IKEA'], 'chair': ['IKEA'], 'sofa': ['IKEA'],
            'light': ['IKEA', 'Philips', 'Xiaomi'], 'blanket': ['IKEA', 'Zara'], 'pillow': ['IKEA', 'Zara'],
            'toys': ['Lego'], 'diapers': ['Pampers'], 'carriage': ['LC Waikiki', 'Zara'], 'dolls': ['Lego', 'Zara'],
            'drill': ['Makita', 'Ronix', 'Bosch'], 'saw': ['Makita', 'Ronix', 'Bosch'], 'welding': ['Ronix', 'Bosch'],
            'pump': ['Makita', 'Ronix'], 'generator': ['Ronix', 'Makita'], 'lawn mower': ['Makita', 'Bosch'],
            'cultivator': ['Makita', 'Bosch'],
            'blender': ['Braun', 'Philips', 'Bosch', 'Tefal'], 'mixer': ['Braun', 'Philips', 'Bosch', 'Tefal'],
            'juicer': ['Braun', 'Philips', 'Panasonic', 'Bosch'], 'meat grinder': ['Panasonic', 'Bosch', 'Philips'],
            'coffee machine': ['Philips', 'Bosch'], 'coffee grinder': ['Bosch', 'Tefal'],
            'toster': ['Tefal', 'Philips', 'Bosch'], 'grill': ['Tefal', 'Bosch', 'Philips'],
            'steam cooker': ['Tefal', 'Philips'], 'iron': ['Philips', 'Tefal', 'Braun'],
            'hair cutter': ['Braun', 'Philips', 'Panasonic'],
            'refrigerators': ['Samsung', 'LG', 'Bosch', 'Snowa'], 'washer': ['LG', 'Samsung', 'Bosch', 'Snowa'],
            'dishwasher': ['Bosch', 'LG', 'Samsung'], 'microwave': ['Samsung', 'LG', 'Panasonic'],
            'vacuum': ['Bosch', 'Philips', 'Panasonic', 'Xiaomi'],
            'tshirt': ['Nike', 'Adidas', 'Zara', 'H&M', 'LC Waikiki'], 'jeans': ['Zara', 'H&M', 'LC Waikiki'],
            'jacket': ['Nike', 'Adidas', 'Zara', 'H&M'], 'shorts': ['Nike', 'Adidas'], 'keds': ['Nike', 'Adidas'],
            'moccasins': ['Zara', 'LC Waikiki'], 'sandals': ['Zara', 'LC Waikiki', 'Nike', 'Adidas'],
            'tennis': ['Nike', 'Adidas'], 'trainer': ['Nike', 'Adidas'], 'bicycle': ['Nike', 'Adidas'],
        }

        ROOT_FALLBACK_BRAND_MAPPING = {
            'apparel': ['Nike', 'Adidas', 'Zara', 'H&M', 'LC Waikiki'], 'sport': ['Nike', 'Adidas'],
            'accessories': ['Zara', 'H&M', 'LC Waikiki', 'Loreal'],
            'appliances': ['LG', 'Bosch', 'Philips', 'Panasonic', 'Snowa', 'Samsung', 'Tefal', 'Braun'],
            'electronics': ['Apple', 'Samsung', 'Sony', 'Xiaomi', 'LG', 'Panasonic', 'Asus', 'JBL', 'Pioneer'],
            'computers': ['Apple', 'Asus', 'Xiaomi', 'MSI', 'Kingston', 'Logitech', 'Western Digital'],
            'kids': ['Lego', 'Pampers', 'LC Waikiki', 'Zara', 'H&M', 'Nestle'],
            'auto': ['Bosch', 'Philips', 'Panasonic', 'Pioneer'],
            'construction': ['Bosch', 'Makita', 'Ronix'], 'medicine': ['Omron', 'Philips', 'Braun'],
            'country yard': ['Bosch', 'Makita', 'Ronix'], 'furniture': ['IKEA', 'Zara', 'H&M'],
            'stationery': ['Xiaomi', 'IKEA', 'Lego'], 'grocery': ['Kalleh', 'Lipton', 'Oila', 'Nestle'],
            'default': ['IKEA', 'Zara', 'Philips', 'Xiaomi']
        }

        # ---------------------------------------------------------
        # REALISTIC PRICE RANGES (Values are in thousands, e.g., 500 = 500,000 Tomans)
        # ---------------------------------------------------------
        PRICE_RANGES = {
            'expensive_tech': (15000, 120000),  # Laptops, TVs, Refrigerators (15M - 120M)
            'mid_tech': (5000, 60000),  # Smartphones, Consoles, Cameras (5M - 60M)
            'small_appliances': (1000, 20000),  # Blenders, PC parts, Headphones (1M - 20M)
            'furniture': (4000, 50000),  # Beds, Sofas (4M - 50M)
            'tools': (2000, 30000),  # Drills, Generators (2M - 30M)
            'apparel_shoes': (400, 6000),  # Clothes, Sneakers (400K - 6M)
            'kids_toys': (300, 15000),  # Toys, Dolls, Baby stuff (300K - 15M)
            'accessories': (150, 3000),  # Wallets, Umbrellas, Belts (150K - 3M)
            'default': (200, 5000)  # Fallback (200K - 5M)
        }

        # Map specific leaf categories to price groups
        LEAF_PRICE_MAPPING = {
            'notebook': 'expensive_tech', 'desktop': 'expensive_tech', 'monitor': 'expensive_tech',
            'refrigerators': 'expensive_tech', 'washer': 'expensive_tech', 'dishwasher': 'expensive_tech',

            'smartphone': 'mid_tech', 'camera': 'mid_tech', 'microwave': 'mid_tech',
            'vacuum': 'mid_tech', 'tablet': 'mid_tech', 'video': 'mid_tech',

            'cpu': 'small_appliances', 'motherboard': 'small_appliances', 'videocards': 'small_appliances',
            'blender': 'small_appliances', 'mixer': 'small_appliances', 'coffee machine': 'small_appliances',
            'toster': 'small_appliances', 'headphone': 'small_appliances', 'iron': 'small_appliances',

            'bed': 'furniture', 'table': 'furniture', 'sofa': 'furniture', 'cabinet': 'furniture',

            'drill': 'tools', 'saw': 'tools', 'generator': 'tools', 'welding': 'tools',

            'tshirt': 'apparel_shoes', 'jeans': 'apparel_shoes', 'jacket': 'apparel_shoes',
            'shoes': 'apparel_shoes', 'keds': 'apparel_shoes', 'bag': 'apparel_shoes',

            'umbrella': 'accessories', 'belt': 'accessories', 'wallet': 'accessories',
            'sunglasses': 'accessories', 'glasses': 'accessories', 'perfume': 'accessories',

            'toys': 'kids_toys', 'dolls': 'kids_toys', 'carriage': 'kids_toys'
        }

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

            # 2. Extract names and root
            cat_clean_name = category.name.strip().lower()
            root_cat = category
            while root_cat.parent is not None:
                root_cat = root_cat.parent
            root_key = root_cat.name.strip().lower()

            # 3. Select matching brands
            if cat_clean_name in SPECIFIC_LEAF_BRAND_MAPPING:
                allowed_brand_names = SPECIFIC_LEAF_BRAND_MAPPING[cat_clean_name]
            else:
                allowed_brand_names = ROOT_FALLBACK_BRAND_MAPPING.get(root_key, ROOT_FALLBACK_BRAND_MAPPING['default'])

            matched_brand_objects = [all_brands[name] for name in allowed_brand_names if name in all_brands]
            if not matched_brand_objects:
                matched_brand_objects = list(all_brands.values())

            # ---------------------------------------------------------
            # DETREMINE PRICE RANGE BASED ON CATEGORY
            # ---------------------------------------------------------
            price_group_key = LEAF_PRICE_MAPPING.get(cat_clean_name)

            # If leaf category is not found in LEAF_PRICE_MAPPING, use root category as fallback
            if not price_group_key:
                if root_key in ['appliances', 'electronics', 'computers']:
                    price_group_key = 'small_appliances'
                elif root_key in ['apparel', 'sport']:
                    price_group_key = 'apparel_shoes'
                elif root_key in ['accessories', 'cosmetics']:
                    price_group_key = 'accessories'
                elif root_key in ['kids']:
                    price_group_key = 'kids_toys'
                elif root_key in ['construction', 'country yard']:
                    price_group_key = 'tools'
                elif root_key in ['furniture']:
                    price_group_key = 'furniture'
                else:
                    price_group_key = 'default'

            min_price, max_price = PRICE_RANGES[price_group_key]

            num_products = CATEGORY_PRODUCT_WEIGHTS.get(cat_clean_name, DEFAULT_PRODUCT_COUNT)

            # 4. Create products
            for _ in range(num_products):
                chosen_brand = random.choice(matched_brand_objects)

                # Generate realistic random price within the selected range (multiplying by 1000)
                price = Decimal(random.randint(min_price, max_price) * 1000)

                model_number = random.randint(100, 999)

                # Determine Discount (25% chance)
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

                # Assign Colors
                if all_colors:
                    product.color.set(random.sample(all_colors, k=random.randint(1, min(3, len(all_colors)))))

                # Assign Sizes
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

                # Create Information entries
                selected_info = random.sample(info_texts, k=random.randint(2, 3))
                for text in selected_info:
                    Information.objects.create(product=product, text=text)

                total_products += 1

            self.stdout.write(
                f'Category "{category.name}" matched with brands: {[b.name for b in matched_brand_objects]} | Price range: {price_group_key}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nExecution complete: Successfully generated {total_products} products with realistic prices.'))