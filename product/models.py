from django.db import models


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
    description = models.TextField()
    price = models.IntegerField()
    discount = models.ManyToManyField(Discount, related_name='products', null=True, blank=True)
    image = models.ImageField(upload_to='product')
    size = models.ManyToManyField(Size, related_name='products', blank=True, null=True)
    color = models.ManyToManyField(Color, related_name='products')

    def __str__(self):
        return f'{self.pk} - {self.title}'

