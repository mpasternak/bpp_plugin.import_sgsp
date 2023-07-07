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
    list_filter = [
        "komorka",
        ("bpp_autor", admin.EmptyFieldListFilter),
    ]
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
    list_filter = [
        "dydaktyczna",
        ("bpp_jednostka", admin.EmptyFieldListFilter),
    ]
    search_fields = list_display


@admin.register(SGSP_Obcy_Autor)
class SGSP_Obcy_AutorAdmin(ReadonlyModelAdmin):
    list_display = ["name"]
    list_filter = [
        ("bpp_autor", admin.EmptyFieldListFilter),
    ]
    search_fields = list_display


@admin.register(SGSP_Journal)
class SGSP_JournalAdmin(ReadonlyModelAdmin):
    list_display = ["journal", "issn", "bpp_zrodlo"]
    list_filter = [
        ("bpp_zrodlo", admin.EmptyFieldListFilter),
    ]
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

    search_fields = list_display[:-1] + [
        "sgsp_artykul_autor__autor__nazwisko",
        "sgsp_artykul_autor__autor__imie",
    ]
    list_filter = [
        "rok_publikacji",
        "jezyk",
        "wersja",
        "licencja",
        ("content_type", admin.EmptyFieldListFilter),
    ]
    inlines = [SGSP_Artykul_AutorInline]
