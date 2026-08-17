from django.contrib import admin
from . import models


class InformationInLine(admin.StackedInline):
    model = models.Information
    extra = 0


class ImageInLine(admin.StackedInline):
    model = models.ProductImage
    extra = 0


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price')
    inlines = [ImageInLine, InformationInLine]


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'date_added', 'last_modified')
    readonly_fields = ('date_added', 'last_modified') # user
    list_filter = ('is_visible', 'date_added', 'last_modified')
    search_fields = ('user__phone', 'product__title', 'text')


# admin.site.register(models.Product)
admin.site.register(models.Discount)
admin.site.register(models.Size)
admin.site.register(models.Color)
# admin.site.register(models.Information)
admin.site.register(models.Brand)
