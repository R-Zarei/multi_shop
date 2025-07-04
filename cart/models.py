from django.db import models
# from account.models import User
# from product.models import Product, Size, Color


# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
#     email = models.EmailField()
#     phone = models.CharField(max_length=11)
#     province = models.CharField(max_length=30)
#     city = models.CharField(max_length=30)
#     address = models.CharField(max_length=300)
#     zipcode = models.CharField(max_length=10)
#
#     def __str__(self):
#         return f'{self.user}'
#
#     def save(self, *args, **kwargs):
#         if not self.phone and self.user:
#             self.phone = self.user.phone
#             super().save(*args, **kwargs)
#
#
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
#     size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='items')
#     color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='items')
