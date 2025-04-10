from django.contrib import admin
from . import models


class InformationAdmin(admin.StackedInline):
    model = models.Information
    extra = 0


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price')
    inlines = [InformationAdmin]


# admin.site.register(models.Product)
admin.site.register(models.Discount)
admin.site.register(models.Size)
admin.site.register(models.Color)
admin.site.register(models.Information)
