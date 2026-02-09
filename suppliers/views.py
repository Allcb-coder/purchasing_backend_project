from rest_framework import generics, permissions

from .models import Supplier, SupplierProduct
from .serializers import SupplierSerializer, SupplierProductSerializer


class SupplierListCreateView(generics.ListCreateAPIView):
    """
    List all active suppliers.
    Allow authenticated users to create suppliers.
    """

    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a supplier.
    """

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]


class SupplierProductListCreateView(generics.ListCreateAPIView):
    """
    List all supplier products.
    Allow authenticated users to link products to suppliers.
    """

    queryset = SupplierProduct.objects.select_related("supplier", "product")
    serializer_class = SupplierProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class SupplierProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a supplier product.
    """

    queryset = SupplierProduct.objects.all()
    serializer_class = SupplierProductSerializer
    permission_classes = [permissions.IsAuthenticated]
