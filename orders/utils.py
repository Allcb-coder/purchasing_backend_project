from django.conf import settings
from django.core.mail import send_mail


def send_order_email_to_admin(order):
    """
    Send an email to the admin notifying them of a new order.
    """
    subject = f"New Order #{order.id}"
    message = (
        f"New order placed by {order.user.email}.\n"
        f"Total amount: ${order.total:.2f}"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )


def send_order_email_to_client(order):
    """
    Send an email to the client confirming their order.
    """
    subject = f"Your Order #{order.id} Confirmation"
    message = (
        f"Hi {order.user.first_name},\n\n"
        f"Thank you for your order #{order.id}!\n"
        f"Total amount: ${order.total:.2f}\n"
        "We will notify you once your order is shipped."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=False,
    )
