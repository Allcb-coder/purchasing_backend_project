from decimal import Decimal

import yaml
from django.db import transaction

from products.models import Category, Product
from suppliers.models import Supplier, SupplierProduct


class YAMLImporter:
    """Universal YAML importer for product data"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.stats = {
            "categories_created": 0,
            "products_created": 0,
            "products_updated": 0,
            "supplier_products_created": 0,
            "supplier_products_updated": 0,
            "errors": 0,
        }

    def log(self, message, style="info"):
        """Log message based on verbosity"""
        if self.verbose:
            print(f"[{style.upper()}] {message}")

    @transaction.atomic
    def import_from_file(self, file_path, supplier_name):
        """Import data from YAML file"""
        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return self.import_data(data, supplier_name)

    @transaction.atomic
    def import_data(self, data, supplier_name):
        """Import data from parsed YAML"""
        # Get or create supplier
        supplier, created = self.get_or_create_supplier(supplier_name)

        # Normalize data structure
        shop_list = self.normalize_data_structure(data)

        # Process each shop
        for shop_data in shop_list:
            self.process_shop(shop_data, supplier)

        return self.stats

    def get_or_create_supplier(self, supplier_name):
        """Get or create supplier"""
        supplier, created = Supplier.objects.get_or_create(
            name=supplier_name,
            defaults={
                "email": f'{supplier_name.lower().replace(" ", "_")}@example.com',
                "address": "Address not specified",
                "phone": "Not specified",
            },
        )

        if created:
            self.log(f"Created new supplier: {supplier_name}", "success")
        else:
            self.log(f"Using existing supplier: {supplier_name}", "warning")

        return supplier, created

    def normalize_data_structure(self, data):
        """Normalize different YAML structures to a common format"""
        if data is None:
            return []

        if isinstance(data, list):
            # Already a list of shops
            return data
        elif isinstance(data, dict):
            # Single shop
            return [data]
        else:
            # Unexpected structure
            self.log(f"Unexpected data type: {type(data)}", "error")
            return []

    def process_shop(self, shop_data, supplier):
        """Process a single shop's data"""
        if not isinstance(shop_data, dict):
            self.log(f"Skipping non-dict shop data: {type(shop_data)}", "warning")
            return

        shop_name = shop_data.get("shop", supplier.name)
        self.log(f"Processing shop: {shop_name}")

        # Extract categories
        categories_map = self.extract_categories(shop_data)

        # Extract products
        products_list = self.extract_products(shop_data)

        # Process products
        for product_data in products_list:
            self.process_product(product_data, supplier, categories_map)

    def extract_categories(self, shop_data):
        """Extract categories from shop data"""
        categories_map = {}

        # Try different possible category structures
        categories = None

        # Case 1: Direct categories list
        if "categories" in shop_data:
            categories = shop_data["categories"]
        elif "Categories" in shop_data:
            categories = shop_data["Categories"]
        elif "category" in shop_data:
            categories = shop_data["category"]

        if categories:
            if isinstance(categories, list):
                for cat_item in categories:
                    self.process_category_item(cat_item, categories_map)
            elif isinstance(categories, dict):
                self.process_category_item(categories, categories_map)
            elif isinstance(categories, str):
                # Single category name
                self.create_category_from_name(categories, categories_map)

        return categories_map

    def process_category_item(self, cat_item, categories_map):
        """Process a single category item"""
        if isinstance(cat_item, dict):
            cat_id = cat_item.get("id")
            cat_name = cat_item.get("name")
            if cat_name:
                category = self.create_or_get_category(cat_name)
                if cat_id:
                    categories_map[cat_id] = category
                categories_map[cat_name] = category
        elif isinstance(cat_item, str):
            self.create_category_from_name(cat_item, categories_map)

    def create_category_from_name(self, cat_name, categories_map):
        """Create category from name string"""
        category = self.create_or_get_category(cat_name)
        categories_map[cat_name] = category

    def create_or_get_category(self, name):
        """Create or get category by name"""
        category, created = Category.objects.get_or_create(name=name.strip())
        if created:
            self.stats["categories_created"] += 1
            self.log(f"Created category: {name}", "success")
        return category

    def extract_products(self, shop_data):
        """Extract products from shop data"""
        products = []

        # Try different product keys
        product_keys = ["goods", "products", "Goods", "Products", "items", "Items"]

        for key in product_keys:
            if key in shop_data:
                items = shop_data[key]
                if isinstance(items, list):
                    products.extend(items)
                elif isinstance(items, dict):
                    products.append(items)
                break

        return products

    def process_product(self, product_data, supplier, categories_map):
        """Process a single product"""
        try:
            if not isinstance(product_data, dict):
                self.log(f"Skipping non-dict product: {type(product_data)}", "warning")
                return

            # Extract basic info
            name = self.extract_value(
                product_data, ["name", "Name", "product", "Product"]
            )
            if not name:
                self.log("Skipping product without name", "warning")
                return

            # Extract category
            category = self.extract_category(product_data, categories_map)

            # Extract price and quantity
            price = self.extract_price(product_data)
            quantity = self.extract_quantity(product_data)

            # Extract description
            description = self.extract_description(product_data)

            # Create or update product
            product = self.create_or_update_product(
                name, category, price, quantity, description
            )

            # Create supplier product link
            self.create_supplier_product(product, supplier, price, quantity)

        except Exception as e:
            self.stats["errors"] += 1
            self.log(f"Error processing product: {str(e)}", "error")

    def extract_value(self, data, keys):
        """Extract value using multiple possible keys"""
        for key in keys:
            if key in data:
                value = data[key]
                if value is not None:
                    if isinstance(value, (int, float)):
                        return str(value)
                    return str(value).strip()
        return None

    def extract_category(self, product_data, categories_map):
        """Extract category from product data"""
        # Try to get category by ID
        for key in ["category", "Category", "category_id", "categoryId"]:
            if key in product_data:
                cat_ref = product_data[key]
                if cat_ref in categories_map:
                    return categories_map[cat_ref]

        # Try to get category by name
        cat_name = self.extract_value(
            product_data, ["category_name", "categoryName", "category_name"]
        )
        if cat_name and cat_name in categories_map:
            return categories_map[cat_name]

        # Default category
        return Category.objects.get_or_create(name="Uncategorized")[0]

    def extract_price(self, product_data):
        """Extract price from product data"""
        price_keys = [
            "price",
            "Price",
            "cost",
            "Cost",
            "unit_price",
            "unitPrice",
            "retail_price",
        ]

        for key in price_keys:
            if key in product_data:
                try:
                    value = product_data[key]
                    if isinstance(value, (int, float, Decimal, str)):
                        return Decimal(str(value))
                except:
                    continue

        return Decimal("0.00")

    def extract_quantity(self, product_data):
        """Extract quantity from product data"""
        qty_keys = [
            "quantity",
            "Quantity",
            "stock",
            "Stock",
            "qty",
            "Qty",
            "count",
            "Count",
        ]

        for key in qty_keys:
            if key in product_data:
                try:
                    value = product_data[key]
                    if isinstance(value, (int, float, str)):
                        return int(float(value))
                except:
                    continue

        return 0

    def extract_description(self, product_data):
        """Extract description from product data"""
        # Direct description
        desc = self.extract_value(
            product_data, ["description", "Description", "desc", "Desc"]
        )
        if desc:
            return desc

        # Build from parameters
        params = None
        for key in ["parameters", "Parameters", "params", "Params", "specs"]:
            if key in product_data:
                params = product_data[key]
                break

        if params:
            if isinstance(params, dict):
                return ", ".join([f"{k}: {v}" for k, v in params.items()])
            elif isinstance(params, str):
                return params

        return ""

    def create_or_update_product(self, name, category, price, quantity, description):
        """Create or update a product"""
        product, created = Product.objects.get_or_create(
            name=name,
            defaults={
                "category": category,
                "price": price,
                "quantity": quantity,
                "description": description,
            },
        )

        if not created:
            # Update existing product
            product.category = category
            product.price = price
            product.quantity = max(product.quantity, quantity)
            if description:
                product.description = description
            product.save()
            self.stats["products_updated"] += 1
            self.log(f"Updated product: {name}", "info")
        else:
            self.stats["products_created"] += 1
            self.log(f"Created product: {name}", "success")

        return product

    def create_supplier_product(self, product, supplier, price, quantity):
        """Create or update supplier product link"""
        supplier_product, created = SupplierProduct.objects.update_or_create(
            supplier=supplier,
            product=product,
            defaults={
                "supplier_price": price,
                "supplier_quantity": quantity,
                "is_available": quantity > 0,
            },
        )

        if created:
            self.stats["supplier_products_created"] += 1
            self.log(f"Created supplier product link: {product.name}", "info")
        else:
            self.stats["supplier_products_updated"] += 1
            self.log(f"Updated supplier product link: {product.name}", "info")
