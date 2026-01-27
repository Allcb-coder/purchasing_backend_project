from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Address

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_person', 'city', 'country', 'is_default')
    list_filter = ('country', 'city', 'is_default')
    search_fields = ('user__username', 'contact_person', 'address_line1', 'city')

# Unregister default User admin and register with custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)