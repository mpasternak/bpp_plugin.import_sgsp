from bpp_plugins.import_sgsp.core import ustaw_nadrzedne_osieroconym_rozdzialom_po_isbn
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        ustaw_nadrzedne_osieroconym_rozdzialom_po_isbn()
