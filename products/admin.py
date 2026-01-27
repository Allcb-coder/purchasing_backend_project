from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
import yaml
from decimal import Decimal
from .models import Category, Product
from suppliers.models import Supplier, SupplierProduct


class ImportYAMLForm(forms.Form):
    supplier = forms.CharField(max_length=200, required=True)
    yaml_data = forms.CharField(widget=forms.Textarea, required=True)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'quantity', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_to_yaml']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-yaml/', self.admin_site.admin_view(self.import_yaml_view), name='import-yaml'),
        ]
        return custom_urls + urls

    def import_yaml_view(self, request):
        """Admin view for importing YAML"""
        if request.method == 'POST':
            form = ImportYAMLForm(request.POST)
            if form.is_valid():
                supplier_name = form.cleaned_data['supplier']
                yaml_data = form.cleaned_data['yaml_data']

                try:
                    data = yaml.safe_load(yaml_data)

                    # Import the data
                    from .views import import_yaml_data
                    stats = import_yaml_data(data, supplier_name)

                    messages.success(
                        request,
                        f"Import successful! "
                        f"Created {stats['products_created']} products, "
                        f"updated {stats['products_updated']} products."
                    )

                    return redirect('..')

                except yaml.YAMLError as e:
                    messages.error(request, f"Invalid YAML: {e}")
                except Exception as e:
                    messages.error(request, f"Import failed: {e}")
        else:
            form = ImportYAMLForm()

        context = {
            'form': form,
            'title': 'Import Products from YAML',
            'opts': self.model._meta,
        }
        return render(request, 'admin/import_yaml.html', context)

    def export_to_yaml(self, request, queryset):
        """Export selected products to YAML format"""
        # This would create a YAML export
        # For now, just show a message
        self.message_user(
            request,
            f"Export functionality for {queryset.count()} products will be implemented."
        )
    export_to_yaml.short_description = "Export selected products to YAML"