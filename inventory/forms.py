
from django import forms

from .models import Category, Product, StockMovement


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Kategoriya nomini kiriting",
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "kategoriya-nomi",
            }),
            "parent": forms.Select(attrs={
                "class": "form-select",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Mahsulot nomini kiriting",
            }),
            "category": forms.Select(attrs={
                "class": "form-select",
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "placeholder": "Mahsulot narxi",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "placeholder": "Boshlang‘ich miqdor",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Mahsulot haqida ma’lumot",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "product",
            "quantity",
            "price",
            "note",
        ]
        widgets = {
            "product": forms.Select(attrs={
                "class": "form-select",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "step": "1",
                "placeholder": "Miqdorni kiriting",
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "placeholder": "Narxni kiriting",
            }),
            "note": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Izoh (ixtiyoriy)",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = (
            Product.objects.filter(is_active=True).order_by("name")
        )

        self.fields["note"].required = False

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity <= 0:
            raise forms.ValidationError(
                "Miqdor 0 dan katta bo‘lishi kerak."
            )

        return quantity

    def clean_price(self):
        price = self.cleaned_data["price"]

        if price < 0:
            raise forms.ValidationError(
                "Narx manfiy bo‘lishi mumkin emas."
            )

        return price
