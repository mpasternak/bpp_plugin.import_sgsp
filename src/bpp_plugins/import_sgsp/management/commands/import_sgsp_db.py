from bpp_plugins.import_sgsp.core import import_sgsp_db
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        import_sgsp_db()
