from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run all initialization management commands in proper sequence for deployment'

    def handle(self, *args, **kwargs):
        commands_sequence = [
            ('import_locations', 'Importing base locations...'),
            ('generate_categories', 'Generating category hierarchy...'),
            ('create_brands', 'Creating brands and linking logos...'),
            ('create_attributes', 'Generating colors, sizes, and discounts...'),
            ('create_mock_products', 'Generating mock products and media...'),
        ]

        self.stdout.write(self.style.WARNING('=== Starting Full Data Initialization ===\n'))

        for cmd_name, step_desc in commands_sequence:
            self.stdout.write(self.style.NOTICE(f'--> Step: {step_desc}'))
            try:
                call_command(cmd_name)
                self.stdout.write(self.style.SUCCESS(f'[DONE] {cmd_name} finished successfully.\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'[FAILED] {cmd_name} failed with error: {str(e)}\n'))
                raise e

        self.stdout.write(self.style.SUCCESS('=== Full Data Initialization Finished Successfully ==='))