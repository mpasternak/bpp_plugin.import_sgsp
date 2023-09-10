import re

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class SGSP_Komorka(models.Model):
    id = models.CharField(max_length=6, primary_key=True)
    nazwa = models.CharField(max_length=512)
    sciezka = models.CharField(max_length=512)
    usos = models.CharField(max_length=10)
    dydaktyczna = models.BooleanField(db_column="kdydaktyczna")

    bpp_jednostka = models.ForeignKey(
        "bpp.Jednostka",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Odpowiednik po stronie BPP",
    )

    def jednostki_nadrzedne(self):
        if not self.sciezka:
            return

        for elem in self.sciezka.split("|"):
            yield SGSP_Komorka.objects.get(id=elem)

    class Meta:
        managed = False
        db_table = "cuvier_komorki"
        verbose_name = "komórka"
        verbose_name_plural = "komórki"


class SGSP_Pracownik(models.Model):
    name = models.TextField(primary_key=True)

    id = models.PositiveSmallIntegerField(unique=True)
    imie = models.CharField(max_length=50)
    nazwisko = models.CharField(max_length=50)
    email = models.EmailField()
    email_sgsp = models.EmailField()

    komorka = models.ForeignKey(
        SGSP_Komorka, on_delete=models.CASCADE, db_column="komorka"
    )
    instytut = models.CharField(max_length=3)

    stopien = models.TextField()
    tytul = models.TextField()
    name_postfix = models.TextField()  # ", prof. uczelni"
    pensum_nowe = models.TextField()

    stanowisko = models.TextField()
    stanowisko_adm = models.TextField()
    stanowisko_adm2 = models.TextField()

    dydaktyczny = models.BooleanField(db_column="dydaktyk")

    zatrudniony_od = models.DateField()
    zatrudniony_do = models.DateField()

    orcid = models.TextField()

    pbn_id = models.IntegerField(db_column="pbnauthor")

    badawcze = models.CharField(max_length=2)
    profil_www = models.TextField()
    konsultacje = models.TextField()
    plec = models.CharField(max_length=1)

    nowe_nazwisko = models.TextField()
    nowe_nazwisko_data = models.DateField()

    bpp_autor = models.ForeignKey(
        "bpp.Autor",
        verbose_name="Odpowiednik po stronie BPP",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "cuvier_pracownicy"
        verbose_name = "pracownik"
        verbose_name_plural = "pracownicy"


class SGSP_Journal(models.Model):
    issn = models.CharField(max_length=9, unique=True, primary_key=True)
    journal = models.CharField(max_length=512)

    bpp_zrodlo = models.ForeignKey(
        "bpp.Zrodlo",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Odpowiednik po stronie BPP",
    )

    class Meta:
        managed = False
        db_table = "cuvier_journals"
        verbose_name = "journal"
        verbose_name_plural = "journale"


class SGSP_Journal_Pkt(models.Model):
    issn = models.ForeignKey(SGSP_Journal, on_delete=models.CASCADE, db_column="issn")
    rok = models.IntegerField()
    pkt = models.IntegerField()

    class Meta:
        managed = False
        db_table = "cuvier_journals_pkt"
        verbose_name = "punkty dla journala"
        verbose_name_plural = "punkty dla journali"


class SGSP_Obcy_Autor(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    name = models.TextField()

    bpp_autor = models.ForeignKey(
        "bpp.Autor",
        verbose_name="Odpowiednik po stronie BPP",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "cuvier_obcy_autorzy"
        verbose_name = "obcy autor"
        verbose_name_plural = "obcy autorzy"


class SGSP_Artykul(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    tytul = models.TextField()
    title = models.TextField()

    jezyk = models.CharField(max_length=2)
    rok_publikacji = models.IntegerField()

    # Uwaga na numer wersji rekordu
    wersja = models.PositiveSmallIntegerField()

    volume = models.TextField()
    issue = models.TextField()
    strona_od = models.TextField()
    strona_do = models.TextField()

    licencja = models.TextField()

    doi = models.TextField()
    issn = models.CharField(max_length=9)

    abstrakt = models.TextField()

    konferencja = models.TextField()
    conf_from = models.DateField()
    conf_to = models.DateField()
    kraj = models.TextField()
    miejscowosc = models.TextField()

    scopus = models.BooleanField()
    wos = models.BooleanField()

    file = models.TextField()

    modifier = models.IntegerField()

    arkusze = models.PositiveSmallIntegerField()
    othercontributors = models.PositiveSmallIntegerField()

    kind = models.TextField(
        null=True,
        blank=True,
        choices=zip(
            ["artykuł", "rozdział", "książka", None],
            ["artykuł", "rozdział", "książka", None],
        ),
    )

    isbn = models.TextField()
    publicationid = models.TextField(help_text="Legacy PBN ID")

    parent_id = models.TextField(db_column="parentid")
    parenttitle = models.TextField()

    wydawca = models.TextField()
    miejsce_wydania = models.TextField()
    wydanie = models.TextField()

    sygnatura = models.TextField()

    url = models.URLField()

    modified = models.DateTimeField()
    ostatni_edytor = models.ForeignKey(
        SGSP_Pracownik, on_delete=models.CASCADE, db_column="ostatni_edytor"
    )

    pkt = models.PositiveSmallIntegerField()
    force_pkt = models.BooleanField()

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, blank=True, null=True
    )
    bpp_rekord = GenericForeignKey()

    class Meta:
        managed = False
        db_table = "cuvier_artykuly"
        verbose_name = "artykuł"
        verbose_name_plural = "artykuły"

    def resolve_parent(self):
        if not self.parent_id:
            return

        if self.parent_id.startswith("PBN-R"):
            # Inna publikacja
            return SGSP_Artykul.get(publicationid=self.parent_id)

        if re.match("\\d\\d\\d\\d-\\d\\d\\d(\\d|X)", self.parent_id.strip()):
            # Zródło
            return SGSP_Journal.objects.get(issn=self.parent_id)

        return self.parent_id

    def __str__(self):
        return str((self.id, self.tytul, self.rok_publikacji, self.parent_id))


class SGSP_Artykul_Autor(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    artykul = models.ForeignKey(
        SGSP_Artykul, on_delete=models.CASCADE, db_column="id_artykulu"
    )
    autor = models.ForeignKey(
        SGSP_Pracownik, on_delete=models.CASCADE, db_column="id_autora", to_field="id"
    )
    kolejnosc = models.PositiveSmallIntegerField()
    obcy = models.BooleanField()
    afiliacja = models.TextField()

    # modifier = models.TextField() # zawsze puste, zignorować
    modified = models.DateField()

    jest_redaktorem = models.BooleanField()
    pbnart = models.TextField()
    pbnauthor = models.TextField()

    ostatni_edytor = models.TextField()

    dyscyplina = models.TextField()

    # d_kandydat1
    # d_kandydat2
    # d_kandydat3

    oswiadczenie = models.BooleanField()

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, blank=True, null=True
    )
    bpp_rekord = GenericForeignKey()

    class Meta:
        managed = False
        db_table = "cuvier_artykul_autor"
        verbose_name = "autor artykułu"
        verbose_name_plural = "autorzy artykułów"

    def get_ostatni_edytor(self):
        if not self.ostatni_edytor:
            return

        try:
            return SGSP_Pracownik.get(name=self.ostatni_edytor)
        except SGSP_Pracownik.DoesNotExist:
            try:
                return SGSP_Pracownik.get(short=self.ostatni_edytor)
            except SGSP_Pracownik.DoesNotExist:
                raise SGSP_Pracownik.DoesNotExist(
                    f"Brak takiego pracownika w bazie jak '{self.ostatni_edytor}'"
                )


class Cuvier_Liczba_N(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    wykladowca_id = models.ForeignKey(
        SGSP_Pracownik,
        to_field="id",
        on_delete=models.CASCADE,
        db_column="wykladowca_id",
    )
    y2017 = models.DecimalField(max_digits=3, decimal_places=2)
    y2018 = models.DecimalField(max_digits=3, decimal_places=2)
    y2019 = models.DecimalField(max_digits=3, decimal_places=2)
    y2020 = models.DecimalField(max_digits=3, decimal_places=2)
    y2021 = models.DecimalField(max_digits=3, decimal_places=2)

    n_od = models.PositiveSmallIntegerField()
    dyscyplina = models.TextField()
    # ybonus = models.TextField() # zawsze puste
    d = models.PositiveSmallIntegerField(help_text="Liczba dyscyplin autora o danym ID")
    n4 = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        help_text="Maksymalna liczba slotów dla danej osoby",
    )

    class Meta:
        managed = False
        db_table = "cuvier_liczba_n"
        verbose_name = "liczba N"
        verbose_name_plural = "liczby N"
