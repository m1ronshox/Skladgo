
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Category, Product, StockMovement
from .forms import CategoryForm, ProductForm, StockMovementForm


# =========================
# BOSH SAHIFA
# =========================

def dashboard(request):
    products_count = Product.objects.count()
    categories_count = Category.objects.count()

    total_quantity = (
        Product.objects.aggregate(total=Sum("quantity"))["total"] or 0
    )

    total_stock_value = sum(
        (product.price or 0) * product.quantity
        for product in Product.objects.all()
    )

    recent_movements = (
        StockMovement.objects.select_related("product")
        .order_by("-created_at")[:10]
    )

    low_stock_products = Product.objects.filter(
        quantity__gt=0,
        quantity__lte=5,
        is_active=True,
    ).order_by("quantity")[:10]

    out_of_stock_products = Product.objects.filter(
        quantity=0,
        is_active=True,
    )[:10]

    context = {
        "products_count": products_count,
        "categories_count": categories_count,
        "total_quantity": total_quantity,
        "total_stock_value": total_stock_value,
        "recent_movements": recent_movements,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
    }

    return render(request, "dashboard.html", context)


# =========================
# MAHSULOTLAR
# =========================

def product_list(request):
    products = Product.objects.select_related("category").order_by("name")

    search = request.GET.get("q", "").strip()
    if search:
        products = products.filter(name__icontains=search)

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all().order_by("name")

    context = {
        "products": products,
        "categories": categories,
        "search": search,
        "selected_category": category_id,
    }

    return render(request, "products.html", context)


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                product = form.save()

                # Boshlang'ich qoldiq uchun kirim tarixini yaratish.
                if product.quantity > 0:
                    StockMovement.objects.create(
                        product=product,
                        quantity=product.quantity,
                        price=product.price,
                        movement_type=StockMovement.IN,
                        note="Mahsulot boshlang'ich qoldig'i",
                    )

            messages.success(request, "Mahsulot muvaffaqiyatli qo'shildi.")
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(
        request,
        "product_form.html",
        {"form": form, "title": "Mahsulot qo'shish"},
    )


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=pk,
    )

    movements = StockMovement.objects.filter(
        product=product
    ).order_by("-created_at")

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "movements": movements,
        },
    )


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Mahsulot ma'lumotlari yangilandi.")
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "product_form.html",
        {
            "form": form,
            "product": product,
            "title": "Mahsulotni tahrirlash",
        },
    )


@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()

    messages.success(request, "Mahsulot o'chirildi.")
    return redirect("product_list")


# =========================
# KATEGORIYALAR
# =========================

def category_list(request):
    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "categories.html",
        {"categories": categories},
    )


def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Kategoriya muvaffaqiyatli qo'shildi.")
            return redirect("category_list")
    else:
        form = CategoryForm()

    return render(
        request,
        "category_form.html",
        {"form": form, "title": "Kategoriya qo'shish"},
    )


# =========================
# OMBORGA KIRIM
# =========================

def stock_in(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data["quantity"]

            with transaction.atomic():
                product = get_object_or_404(
                    Product.objects.select_for_update(),
                    pk=form.cleaned_data["product"].pk,
                    is_active=True,
                )

                movement = form.save(commit=False)
                movement.product = product
                movement.movement_type = StockMovement.IN
                movement.price = form.cleaned_data["price"]
                movement.save()

                Product.objects.filter(pk=product.pk).update(
                    quantity=F("quantity") + quantity
                )

            messages.success(request, "Mahsulot omborga kirim qilindi.")
            return redirect("stock_history")
    else:
        form = StockMovementForm()

    return render(
        request,
        "stock_form.html",
        {"form": form, "title": "Omborga kirim"},
    )


# =========================
# OMBORDAN CHIQIM
# =========================

def stock_out(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data["quantity"]

            with transaction.atomic():
                product = get_object_or_404(
                    Product.objects.select_for_update(),
                    pk=form.cleaned_data["product"].pk,
                    is_active=True,
                )

                # Omborda yetarli mahsulot borligini tekshirish.
                updated = Product.objects.filter(
                    pk=product.pk,
                    quantity__gte=quantity,
                ).update(
                    quantity=F("quantity") - quantity
                )

                if updated == 0:
                    form.add_error(
                        "quantity",
                        "Omborda bu miqdorda mahsulot mavjud emas.",
                    )
                else:
                    movement = form.save(commit=False)
                    movement.product = product
                    movement.movement_type = StockMovement.OUT
                    movement.price = form.cleaned_data["price"]
                    movement.save()

                    messages.success(
                        request,
                        "Mahsulot ombordan chiqarildi.",
                    )
                    return redirect("stock_history")
    else:
        form = StockMovementForm()

    return render(
        request,
        "stock_form.html",
        {"form": form, "title": "Ombordan chiqim"},
    )


# =========================
# KIRIM-CHIQIM TARIXI
# =========================

def stock_history(request):
    movements = (
        StockMovement.objects.select_related("product")
        .order_by("-created_at")
    )

    movement_type = request.GET.get("type")
    if movement_type in (
        StockMovement.IN,
        StockMovement.OUT,
    ):
        movements = movements.filter(movement_type=movement_type)

    context = {
        "movements": movements,
        "selected_type": movement_type,
    }

    return render(request, "stock_history.html", context)
