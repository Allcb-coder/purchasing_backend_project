from decimal import Decimal
import yaml
from django.db.models import Count
from django.core.files.storage import default_storage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for product categories
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]
    ordering = ["name"]

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        """Get all active products for this category"""
        category = self.get_object()
        products = category.products.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def categories_summary(self, request):
        """
        Summary of categories with count of products
        """
        categories = Category.objects.annotate(product_count=Count("products"))
        data = [
            {"id": cat.id, "name": cat.name, "product_count": cat.product_count}
            for cat in categories
            if cat.product_count > 0
        ]
        return Response(data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD for products with filtering, search, and ordering
    """

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "created_at", "quantity"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by price range
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by in-stock
        in_stock = self.request.query_params.get("in_stock")
        if in_stock and in_stock.lower() == "true":
            queryset = queryset.filter(quantity__gt=0)

        return queryset

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Return first 10 featured products"""
        featured_products = self.get_queryset()[:10]
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def import_yaml(request):
    """
    Admin-only endpoint to import categories and products from a YAML file.
    Expects uploaded file in 'file' field.
    """
    if "file" not in request.FILES:
        return Response(
            {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    file = request.FILES["file"]
    supplier_name = request.data.get("supplier", "Imported Supplier")  # for future use

    try:
        # Read YAML content
        content = file.read().decode("utf-8")
        data = yaml.safe_load(content)

        imported_count = 0

        if isinstance(data, list):
            for shop in data:
                if isinstance(shop, dict):
                    # Process categories
                    categories = {}
                    for cat_data in shop.get("categories", []):
                        if isinstance(cat_data, dict):
                            cat_id = cat_data.get("id")
                            cat_name = cat_data.get("name")
                            if cat_name:
                                category, _ = Category.objects.get_or_create(name=cat_name)
                                categories[cat_id] = category

                    # Process products
                    for product_data in shop.get("goods", []):
                        if isinstance(product_data, dict):
                            name = product_data.get("name")
                            category_id = product_data.get("category")
                            price = product_data.get("price", 0)

                            if name and category_id in categories:
                                product, created = Product.objects.get_or_create(
                                    name=name,
                                    defaults={
                                        "category": categories[category_id],
                                        "price": Decimal(str(price)),
                                        "quantity": product_data.get("quantity", 0),
                                        "description": str(
                                            product_data.get("parameters", {})
                                        ),
                                    },
                                )
                                if created:
                                    imported_count += 1

        return Response(
            {
                "success": True,
                "message": f"Successfully imported {imported_count} products",
                "count": imported_count,
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
