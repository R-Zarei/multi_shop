from django.db import models
from account.models import User, Address
from product.models import Product, Size, Color
from django.utils import timezone
from datetime import timedelta


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='orders')
    is_paid = models.BooleanField(default=False)
    date_ordered = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='items')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveSmallIntegerField(default=1)


def get_default_valid_untile():
    return timezone.now() + timedelta(days=1)

class DiscountCode(models.Model):
    title =  models.CharField(max_length=120)
    code = models.CharField(max_length=120, unique=True)
    percentage = models.PositiveSmallIntegerField(default=0)
    quantity = models.PositiveSmallIntegerField(default=1)
    valid_until = models.DateTimeField(default=get_default_valid_untile())
    users = models.ManyToManyField(User, through='DiscountCodeUsage', related_name="discount_codes", blank=True)

    def __str__(self):
        return self.title


class DiscountCodeUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    discount = models.ForeignKey(DiscountCode, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'discount')