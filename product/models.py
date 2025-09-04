import uuid
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


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
    percentage = models.SmallIntegerField()

    def __str__(self):
        return self.title


class Information(models.Model):
    text = models.TextField()
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='information')

    def __str__(self):
        return f'{self.product} - {self.text[:20]}'


class Product(models.Model):
    title = models.CharField(max_length=100)
    external_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.ManyToManyField(Discount, related_name='products', blank=True)
    image = models.ImageField(upload_to='product')
    size = models.ManyToManyField(Size, related_name='products', blank=True)
    color = models.ManyToManyField(Color, related_name='products')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolut_url(self):
        return reverse('product:product_detail', kwargs={'external_id': self.external_id ,'slug': self.slug})

    def __str__(self):
        return f'{self.pk} - {self.title}'

