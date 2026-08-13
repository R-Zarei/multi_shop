from django.db import models
from account.models import User, Address
from product.models import Product, Size, Color, Discount
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
import random


def get_default_valid_untile():
    return timezone.now() + timedelta(days=1)

class DiscountCode(models.Model):
    title =  models.CharField(max_length=120)
    code = models.CharField(max_length=120, unique=True)
    percentage = models.PositiveSmallIntegerField(default=0)
    quantity = models.PositiveSmallIntegerField(default=1)
    valid_until = models.DateTimeField(default=get_default_valid_untile)
    users = models.ManyToManyField(User, through='DiscountCodeUsage', related_name="discount_codes", blank=True)

    def __str__(self):
        return self.title


def generate_order_code():
    # (YYMMDD) date 6 digit
    date_part = timezone.now().strftime("%y%m%d")
    # 4 digit randomly
    random_part = ''.join(random.choices('0123456789', k=4))
    code = f"{date_part}{random_part}"

    # if it is duplicate, it will reproduce.
    while Order.objects.filter(code=code).exists():
        random_part = ''.join(random.choices('0123456789', k=4))
        code = f"{date_part}{random_part}"

    return code


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        PROCESSING = 'processing'
        # SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered'
        CANCELED = 'canceled'
        RETURNED = 'returned'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    code = models.CharField(max_length=10, unique=True, editable=False, verbose_name='Order Code')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='orders')
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    date_ordered = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.CASCADE, null=True, blank=True,  related_name='orders')
    final_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    EXPIRATION_HOURS = 0.25

    def is_expired(self):
        return (not self.is_paid) and timezone.now() > self.date_ordered + timedelta(hours=self.EXPIRATION_HOURS)

    def get_absolute_url(self):
        return reverse("account:order_details", kwargs={"order_code": self.code})

    def __str__(self):
        return f'{self.code}'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_order_code()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='items')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True, blank=True, related_name='order_items')
    quantity = models.PositiveSmallIntegerField(default=1)

    @property
    def total_price(self):
        price = self.price
        if self.discount:
            price = self.price - (self.price * self.discount.percentage / 100)
        return price * self.quantity


class DiscountCodeUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    discount = models.ForeignKey(DiscountCode, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, related_name="discount_code_usage")
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'discount')