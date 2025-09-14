from django.contrib import admin
from .models import Order, OrderItem, DiscountCode, DiscountCodeUsage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'is_paid')
    list_filter = ('is_paid',)
    inlines = (OrderItemInline,)

class DiscountCodeUsageInline(admin.TabularInline):
    model = DiscountCodeUsage
    extra = 0

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'percentage', 'code', 'quantity')
    inlines = (DiscountCodeUsageInline,)