from bpp_plugins.import_sgsp.models import (
    SGSP_Artykul,
    SGSP_Artykul_Autor,
    SGSP_Journal,
    SGSP_Komorka,
    SGSP_Obcy_Autor,
    SGSP_Pracownik,
)
from django.contrib import admin
from rozbieznosci_dyscyplin.admin import ReadonlyAdminMixin


class ReadonlyModelAdmin(ReadonlyAdminMixin, admin.ModelAdmin):
    pass


@admin.register(SGSP_Pracownik)
class SGSP_PracownikAdmin(ReadonlyModelAdmin):
    list_display = ["nazwisko", "imie", "email", "email_sgsp", "komorka"]
    search_fields = [
        "nazwisko",
        "imie",
        "email",
        "email_sgsp",
        "komorka__nazwa",
        "komorka__skrot",
    ]


@admin.register(SGSP_Komorka)
class SGSP_KomorkaAdmin(ReadonlyModelAdmin):
    list_display = ["nazwa", "sciezka", "usos"]
    list_filter = ["dydaktyczna"]
    search_fields = list_display


@admin.register(SGSP_Obcy_Autor)
class SGSP_Obcy_AutorAdmin(ReadonlyModelAdmin):
    list_display = ["name"]
    search_fields = list_display


@admin.register(SGSP_Journal)
class SGSP_JournalAdmin(ReadonlyModelAdmin):
    list_display = ["journal", "issn", "bpp_zrodlo"]
    search_fields = list_display


class SGSP_Artykul_AutorInline(admin.TabularInline):
    model = SGSP_Artykul_Autor


@admin.register(SGSP_Artykul)
class SGSP_ArtykulAdmin(ReadonlyModelAdmin):
    list_display = [
        "tytul",
        "title",
        "jezyk",
        "rok_publikacji",
        "konferencja",
        "parent_id",
        "parenttitle",
        "bpp_rekord",
    ]

    search_fields = list_display
    list_filter = ["rok_publikacji", "jezyk", "wersja", "licencja"]
    inlines = [SGSP_Artykul_AutorInline]
