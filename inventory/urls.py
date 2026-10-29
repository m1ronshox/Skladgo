
from django.urls import path
from . import views


urlpatterns = [
    # Bosh sahifa
    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    # Mahsulotlar
    path(
        'products/',
        views.product_list,
        name='product_list'
    ),
    path(
        'products/add/',
        views.product_create,
        name='product_create'
    ),
    path(
        'products/<int:pk>/',
        views.product_detail,
        name='product_detail'
    ),
    path(
        'products/<int:pk>/edit/',
        views.product_edit,
        name='product_edit'
    ),
    path(
        'products/<int:pk>/delete/',
        views.product_delete,
        name='product_delete'
    ),

    # Kategoriyalar
    path(
        'categories/',
        views.category_list,
        name='category_list'
    ),
    path(
        'categories/add/',
        views.category_create,
        name='category_create'
    ),

    # Mahsulot kirimi
    path(
        'stock/in/',
        views.stock_in,
        name='stock_in'
    ),

    # Mahsulot chiqimi
    path(
        'stock/out/',
        views.stock_out,
        name='stock_out'
    ),

    # Kirim-chiqim tarixi
    path(
        'stock/history/',
        views.stock_history,
        name='stock_history'
    ),
]
