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

    # Only categories that have no children are displayed in the selection list.
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = models.Category.objects.filter(children__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'date_added', 'last_modified')
    readonly_fields = ('date_added', 'last_modified') # user
    list_filter = ('is_visible', 'date_added', 'last_modified')
    search_fields = ('user__phone', 'product__title', 'text')


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_path', 'is_active')
    readonly_fields = ('created_at',)
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    readonly_fields = ('created_at',)
    list_filter = ('is_active',)
    search_fields = ('name',)



# admin.site.register(models.Product)
admin.site.register(models.Discount)
admin.site.register(models.Size)
admin.site.register(models.Color)
# admin.site.register(models.Information)
# admin.site.register(models.Brand)
