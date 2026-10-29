from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Kategoriya nomi"
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True,
        verbose_name="Slug"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name="Asosiy kategoriya"
    )

    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name="Rasm"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Kategoriya"
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Mahsulot nomi"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Tavsif"
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Narx"
    )

    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Ombordagi miqdor"
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name="Rasm"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self):
        return self.name

    @property
    def stock_status(self):
        if self.quantity == 0:
            return "Tugagan"

        if self.quantity <= 5:
            return "Kam qolgan"

        return "Mavjud"


class StockMovement(models.Model):

    IN = 'IN'
    OUT = 'OUT'

    MOVEMENT_TYPES = [
        (IN, 'Kirim'),
        (OUT, 'Chiqim'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name="Mahsulot"
    )

    movement_type = models.CharField(
        max_length=3,
        choices=MOVEMENT_TYPES,
        verbose_name="Harakat turi"
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Miqdor"
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Narx"
    )

    note = models.TextField(
        blank=True,
        verbose_name="Izoh"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ombor harakati"
        verbose_name_plural = "Ombor harakatlari"

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}"