from django.contrib import admin
from .models import Category, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'parent',
        'created_at',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'parent',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'quantity',
        'stock_status',
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
    )

    list_filter = (
        'category',
        'is_active',
    )

    list_editable = (
        'is_active',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'movement_type',
        'quantity',
        'price',
        'created_at',
    )

    search_fields = (
        'product__name',
        'note',
    )

    list_filter = (
        'movement_type',
        'created_at',
    )

    readonly_fields = (
        'created_at',
    )