import os
import sys
from django.core.management.base import BaseCommand
from products.utils.yaml_importer import YAMLImporter


class Command(BaseCommand):
    help = 'Import products from YAML file using universal importer'

    def add_arguments(self, parser):
        parser.add_argument(
            'yaml_file',
            type=str,
            help='Path to the YAML file to import'
        )
        parser.add_argument(
            '--supplier',
            type=str,
            required=True,
            help='Supplier name for the imported products'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output for debugging'
        )

    def handle(self, *args, **options):
        yaml_file = options['yaml_file']
        supplier_name = options['supplier']
        verbose = options['verbose']

        if not os.path.exists(yaml_file):
            self.stdout.write(self.style.ERROR(f'File {yaml_file} does not exist'))
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS(f'Importing from {yaml_file} for supplier {supplier_name}'))

        try:
            importer = YAMLImporter(verbose=verbose)
            stats = importer.import_from_file(yaml_file, supplier_name)

            # Print summary
            self.print_summary(stats)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during import: {e}'))
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def print_summary(self, stats):
        """Print import summary"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('IMPORT SUMMARY:'))
        self.stdout.write(self.style.SUCCESS(f'Categories created: {stats["categories_created"]}'))
        self.stdout.write(self.style.SUCCESS(f'Products created: {stats["products_created"]}'))
        self.stdout.write(self.style.SUCCESS(f'Products updated: {stats["products_updated"]}'))
        self.stdout.write(self.style.SUCCESS(f'Supplier products created: {stats["supplier_products_created"]}'))
        self.stdout.write(self.style.SUCCESS(f'Supplier products updated: {stats["supplier_products_updated"]}'))

        if stats['errors'] > 0:
            self.stdout.write(self.style.WARNING(f'Errors encountered: {stats["errors"]}'))

        self.stdout.write(self.style.SUCCESS('='*50))