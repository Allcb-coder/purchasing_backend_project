from decimal import Decimal

from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from cart.models import Cart

from .models import Order, OrderItem
from .serializers import OrderSerializer
from .utils import send_order_email_to_admin, send_order_email_to_client


class OrderListView(generics.ListCreateAPIView):
    """
    API view to list all orders of the authenticated user
    and create a new order from the user's cart.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.items.count() == 0:
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    first_name=request.data.get("first_name", ""),
                    last_name=request.data.get("last_name", ""),
                    email=request.data.get("email", request.user.email),
                    phone=request.data.get("phone", ""),
                    address=request.data.get("address", ""),
                    city=request.data.get("city", ""),
                    postal_code=request.data.get("postal_code", ""),
                    country=request.data.get("country", ""),
                    notes=request.data.get("notes", ""),
                    status="NEW",
                )

                # Create order items and calculate subtotal
                total_amount = Decimal("0.00")
                for cart_item in cart.items.all():
                    unit_price = cart_item.product.price
                    total_price = unit_price * cart_item.quantity

                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        product_name=cart_item.product.name,
                    )

                    total_amount += total_price

                # Calculate totals
                order.subtotal = total_amount
                order.tax = total_amount * Decimal("0.10")  # 10% tax
                order.shipping_cost = (
                    Decimal("10.00") if total_amount < Decimal("100.00") else Decimal("0.00")
                )
                order.total = order.subtotal + order.tax + order.shipping_cost
                order.save()

                # Clear cart
                cart.items.all().delete()

                # Send emails (admin + client)
                try:
                    send_order_email_to_admin(order)
                    send_order_email_to_client(order)
                except Exception as email_error:
                    # Email failure should NOT cancel order creation
                    print(f"Email sending failed: {email_error}")

                return Response(
                    OrderSerializer(order).data,
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OrderDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve details of a single order
    belonging to the authenticated user.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
