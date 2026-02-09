from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile for additional information"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="User",
    )

    # Contact information
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone")
    company_name = models.CharField(
        max_length=200, blank=True, verbose_name="Company Name"
    )

    # Address information
    shipping_address = models.TextField(blank=True, verbose_name="Shipping Address")
    shipping_city = models.CharField(max_length=100, blank=True, verbose_name="City")
    shipping_postal_code = models.CharField(
        max_length=20, blank=True, verbose_name="Postal Code"
    )
    shipping_country = models.CharField(
        max_length=100, blank=True, verbose_name="Country"
    )

    # Preferences
    receive_email_notifications = models.BooleanField(
        default=True, verbose_name="Email Notifications"
    )
    receive_sms_notifications = models.BooleanField(
        default=False, verbose_name="SMS Notifications"
    )

    # Metadata
    email_confirmed = models.BooleanField(default=False, verbose_name="Email Confirmed")
    registration_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Registration Date"
    )
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Last Activity")

    # User type (customer or supplier)
    USER_TYPE_CHOICES = [
        ("CUSTOMER", "Customer"),
        ("SUPPLIER", "Supplier"),
        ("ADMIN", "Administrator"),
    ]
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="CUSTOMER",
        verbose_name="User Type",
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile of {self.user.email}"

    def get_full_name(self):
        """Get user's full name"""
        return (
            f"{self.user.first_name} {self.user.last_name}".strip()
            or self.user.username
        )

    @property
    def has_complete_profile(self):
        """Check if user has completed their profile"""
        return all(
            [
                self.user.first_name,
                self.user.last_name,
                self.phone,
                self.shipping_address,
            ]
        )


# Signal to create user profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# Signal to create cart when a new user is created
@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        from cart.models import Cart

        Cart.objects.create(user=instance)


class Address(models.Model):
    """User addresses for shipping"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="User",
    )

    # Address details
    address_type = models.CharField(
        max_length=20,
        choices=[("HOME", "Home"), ("WORK", "Work"), ("OTHER", "Other")],
        default="HOME",
        verbose_name="Address Type",
    )

    # Contact person at this address
    contact_person = models.CharField(max_length=200, verbose_name="Contact Person")
    contact_phone = models.CharField(max_length=20, verbose_name="Contact Phone")

    # Address lines
    address_line1 = models.CharField(max_length=200, verbose_name="Address Line 1")
    address_line2 = models.CharField(
        max_length=200, blank=True, verbose_name="Address Line 2"
    )
    city = models.CharField(max_length=100, verbose_name="City")
    state = models.CharField(max_length=100, blank=True, verbose_name="State/Province")
    postal_code = models.CharField(max_length=20, verbose_name="Postal Code")
    country = models.CharField(max_length=100, verbose_name="Country")

    # Address metadata
    is_default = models.BooleanField(default=False, verbose_name="Default Address")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.contact_person}, {self.address_line1}, {self.city}"

    def save(self, *args, **kwargs):
        """If this is set as default, unset default for other addresses"""
        if self.is_default:
            # Update other addresses of this user to not be default
            Address.objects.filter(user=self.user, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)
        super().save(*args, **kwargs)

    def get_full_address(self):
        """Get formatted full address"""
        lines = [
            self.address_line1,
            self.address_line2,
            f"{self.city}, {self.state}".strip(", "),
            self.postal_code,
            self.country,
        ]
        return ", ".join(filter(None, lines))
