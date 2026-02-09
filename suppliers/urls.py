from django.urls import path

from .views import (
    SupplierListCreateView,
    SupplierDetailView,
    SupplierProductListCreateView,
    SupplierProductDetailView,
)

app_name = "suppliers"

urlpatterns = [
    # Suppliers
    path(
        "",
        SupplierListCreateView.as_view(),
        name="supplier-list-create",
    ),
    path(
        "<int:pk>/",
        SupplierDetailView.as_view(),
        name="supplier-detail",
    ),
    # Supplier products
    path(
        "products/",
        SupplierProductListCreateView.as_view(),
        name="supplier-product-list-create",
    ),
    path(
        "products/<int:pk>/",
        SupplierProductDetailView.as_view(),
        name="supplier-product-detail",
    ),
]
