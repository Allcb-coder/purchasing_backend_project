from django.urls import path
from .views import OrderListView, OrderDetailView

app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="order-list-create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
