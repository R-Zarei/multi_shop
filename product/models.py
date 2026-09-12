import uuid
from unicodedata import category

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from account.models import User


class Size(models.Model):
    title = models.CharField(max_length=10)

    def __str__(self):
        return self.title


class Color(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Discount(models.Model):
    title = models.CharField(max_length=50)
    percentage = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def is_active(self):
        return self.start_date <= timezone.localdate() <= self.end_date

    def __str__(self):
        return self.title


class Information(models.Model):
    text = models.TextField()
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='information')

    def __str__(self):
        return f'{self.product} - {self.text[:20]}'


class Product(models.Model):
    title = models.CharField(max_length=100)
    brand = models.ForeignKey('Brand', on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='products')
    external_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=14, decimal_places=2)
    discount = models.ForeignKey(Discount, related_name='products', blank=True, null=True, on_delete=models.SET_NULL)
    size = models.ManyToManyField(Size, related_name='products', blank=True)
    color = models.ManyToManyField(Color, related_name='products')

    @property
    def final_price(self):
        if self.discount and self.discount.is_active:
            return self.price - (self.price * Decimal(self.discount.percentage) / Decimal("100"))
        return self.price

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product:product_detail', kwargs={'external_id': self.external_id ,'slug': self.slug})

    def __str__(self):
        return f'{self.pk} - {self.title}'


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name='comments')
    text = models.TextField(max_length=500)
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.pk} - {self.product} - {self.user}'


def product_image_path(instance, filename):
    return f'product/{instance.product.external_id}/{filename}'

class ProductImage(models.Model):
    image = models.ImageField(upload_to=product_image_path)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f'{self.pk} - {self.product}'


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brand', blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('product:brand_product_list', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.pk} - {self.name}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=201, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True, related_name='children')
    image = models.ImageField(upload_to='categorise', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('product:category_product_list', kwargs={'slug': self.slug})

    def get_full_path(self):
        names = [self.name]
        parent = self.parent
        while parent is not None:
            names.append(parent.name)
            parent = parent.parent
        # noinspection unreachable-code
        return ' > '.join(reversed(names))

    def __str__(self):
        return f'{self.pk} - {self.get_full_path()}'

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        if self.parent:
            slug = f"{slugify(self.parent.name)}-{slug}"

        self.slug = slug
        super().save(*args, **kwargs)
