import datetime
import re
import warnings


def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return str(msg) + "\n"


warnings.formatwarning = custom_formatwarning

from bpp.models import (
    ILOSC_ZNAKOW_NA_ARKUSZ,
    Autor,
    Autor_Jednostka,
    Charakter_Formalny,
    Funkcja_Autora,
    Grupa_Pracownicza,
    Jednostka,
    Jednostka_Wydzial,
    Jezyk,
    Konferencja,
    Plec,
    Rodzaj_Zrodla,
    Status_Korekty,
    Typ_KBN,
    Typ_Odpowiedzialnosci,
    Tytul,
    Uczelnia,
    Wydawnictwo_Ciagle,
    Wydawnictwo_Ciagle_Autor,
    Wydawnictwo_Zwarte,
    Wydawnictwo_Zwarte_Autor,
    Wydzial,
    Zrodlo,
)
from bpp_plugins.import_sgsp.models import (
    SGSP_Artykul,
    SGSP_Artykul_Autor,
    SGSP_Journal,
    SGSP_Komorka,
    SGSP_Obcy_Autor,
    SGSP_Pracownik,
)
from django.db import DataError, IntegrityError
from import_common.core import matchuj_wydawce

JEDNOSTKA_DOMYSLNA_SGSP = "Jednostka domyślna SGSP"
OBCY_AUTORZY_ID_START = 2000


def import_journals():
    journal: SGSP_Journal
    periodyk = Rodzaj_Zrodla.objects.get(id=1)
    for journal in SGSP_Journal.objects.all():
        Zrodlo.objects.get_or_create(
            nazwa=journal.journal,
            skrot=journal.journal,
            issn=journal.issn,
            rodzaj=periodyk,
        )


def import_komorki(uczelnia, wydzial):
    struktura = {}

    komorka: SGSP_Komorka
    for komorka in SGSP_Komorka.objects.all():
        jednostka = Jednostka.objects.get_or_create(
            nazwa=komorka.nazwa,
            skrot=komorka.id,
            wydzial=wydzial,
            uczelnia=uczelnia,
        )[0]
        struktura[komorka.id] = komorka.sciezka

        Jednostka_Wydzial.objects.get_or_create(jednostka=jednostka, wydzial=wydzial)

    jednostka: Jednostka
    for jednostka in Jednostka.objects.all():
        if jednostka.skrot not in struktura:
            continue

        rodzice = struktura[jednostka.skrot]
        if not rodzice:
            continue

        nadrzedna = rodzice.split("|")[-1]
        try:
            jednostka.parent = Jednostka.objects.get(skrot=nadrzedna)
        except Jednostka.DoesNotExist:
            print(f"[SGSPJ1] Brak jednostki nadrzednej dla kodu {nadrzedna}")
        jednostka.save()


def import_users():
    pracownik: SGSP_Pracownik
    for pracownik in SGSP_Pracownik.objects.all():
        tytul = None
        if pracownik.tytul:
            tytul = Tytul.objects.get_or_create(
                skrot=pracownik.tytul, defaults={"nazwa": pracownik.tytul}
            )[0]

        autor = Autor.objects.get_or_create(
            pk=pracownik.id,
            imiona=pracownik.imie or "",
            nazwisko=pracownik.nowe_nazwisko or pracownik.nazwisko or "'",
            tytul=tytul,
            pseudonim=pracownik.name_postfix or None,
            email=pracownik.email_sgsp,
            plec=Plec.objects.get(skrot=pracownik.plec)
            if pracownik.plec is not None
            else None,
            orcid=pracownik.orcid,
            poprzednie_nazwiska=pracownik.nazwisko
            if pracownik.nowe_nazwisko is not None
            else None,
            adnotacje=pracownik.konsultacje or "",
            opis=pracownik.profil_www,
        )[0]

        if pracownik.komorka_id is None:
            continue

        profesor_uczelni = Funkcja_Autora.objects.get_or_create(
            nazwa="profesor uczelni", defaults={"pokazuj_za_nazwiskiem": True}
        )[0]

        SGSP_PROFESOR_UCZELNI = ", prof. uczelni"

        funkcja_w_jednostce = None
        if pracownik.name_postfix == SGSP_PROFESOR_UCZELNI:
            funkcja_w_jednostce = profesor_uczelni

        if pracownik.stanowisko == "profesor uczelni":
            funkcja_w_jednostce = profesor_uczelni
        else:
            if pracownik.stanowisko:
                if pracownik.stanowisko is not None and funkcja_w_jednostce is not None:
                    warnings.warn(
                        f"[SGSPA2] Dla pracownika {autor} funkcja w jednostce to profesor uczelni, "
                        f"ale nadpiszę to {pracownik.stanowisko}"
                    )
                funkcja_w_jednostce = Funkcja_Autora.objects.get_or_create(
                    nazwa=pracownik.stanowisko, defaults={"skrot": pracownik.stanowisko}
                )[0]

        try:
            zatrudniony_do = pracownik.zatrudniony_do
            if zatrudniony_do in [
                datetime.date(9999, 12, 31),
                datetime.date(9999, 1, 1),
                datetime.date(2030, 9, 30),
            ]:
                zatrudniony_do = None

            Autor_Jednostka.objects.get_or_create(
                autor=autor,
                jednostka=Jednostka.objects.get(skrot=pracownik.komorka_id),
                funkcja=funkcja_w_jednostce,
                rozpoczal_prace=pracownik.zatrudniony_od,
                zakonczyl_prace=zatrudniony_do,
                grupa_pracownicza=Grupa_Pracownicza.objects.get_or_create(
                    nazwa=pracownik.badawcze
                )[0]
                if pracownik.badawcze
                else None,
            )
        except Jednostka.DoesNotExist:
            warnings.warn(
                f"[SGSPA1] Autor {autor} pracuje w jednostce {pracownik.komorka_id} ale nie ma takiej w bazie BPP"
            )


def znajdz_rekord_po_stronie_bpp(artykul_id: int):
    try:
        return Wydawnictwo_Zwarte.objects.get(pk=artykul_id)
    except Wydawnictwo_Zwarte.DoesNotExist:
        try:
            return Wydawnictwo_Ciagle.objects.get(pk=artykul_id)
        except Wydawnictwo_Ciagle.DoesNotExist:
            pass


def importuj_pojedynczy_artykul(artykul: SGSP_Artykul):
    rekord = znajdz_rekord_po_stronie_bpp(artykul.id)
    if rekord is not None:
        return rekord

    # Obsługiwane
    #  id                | integer                     |           | not null | nextval('cuvier_artykuly_id_seq'::regcl
    #  pkt               | integer                     |           |          |
    #  tytul             | text                        |           |          |
    #  title             | text                        |           |          |
    #  jezyk             | text                        |           |          |
    #  rok_publikacji    | integer                     |           |          |
    #  wydawca           | text                        |           |          |
    #  miejsce_wydania   | text                        |           |          |
    #  strona_od         | integer                     |           |          |
    #  strona_do         | integer                     |           |          |
    #  volume            | text                        |           |          |
    #  doi               | text                        |           |          |
    #  konferencja       | text                        |           |          |
    #  scopus            | text                        |           |          |
    #  wos               | text                        |           |          |
    #  conf_from         | date                        |           |          |
    #  conf_to           | date                        |           |          |
    #  kraj              | text                        |           |          |
    #  miejscowosc       | text                        |           |          |
    #  url               | text                        |           |          |
    #  kind              | text                        |           |          |
    #  issn              | text                        |           |          |
    #  publicationid     | text                        |           |          |
    #  abstrakt          | text                        |           |          |
    #  arkusze           | integer                     |           |          |
    #  parentid          | text                        |           |          |
    #  parenttitle       | text                        |           |          |

    # Tylko dla zwartych
    #  isbn              | text                        |           |          |

    # TODO:
    #  issue             | text                        |           |          |
    #  licencja          | text                        |           |          |
    #  uswiecony         | text                        |           |          |
    #  file              | text                        |           |          |
    #  modifier          | integer                     |           |          |
    #  othercontributors | integer                     |           |          |
    #  wydanie           | text                        |           |          |
    #  sygnatura         | text                        |           |          |

    # Ignorowane
    #  force_pkt         | integer                     |           |
    #  wersja            | text                        |           |          |
    #  ostatni_edytor    | text                        |           |          |
    #  modified          | timestamp without time zone |           | not null | now()

    translacja_jezykow = {
        "pl": ("pol.", None),
        "en": ("ang.", None),
        "cz": ("cze.", "czeski"),
        "ru": ("ros.", "rosyjski"),
        "de": ("niem.", "niemiecki"),
        "uk": ("ukr.", "ukraiński"),
        "bg": ("bułg.", "bułgarski"),
    }

    adnotacje = ""

    jezyk = None

    if transl := translacja_jezykow.get(artykul.jezyk, None):
        skrot, nazwa = transl
        jezyk = Jezyk.objects.get_or_create(skrot=skrot, defaults={"nazwa": nazwa})[0]

    if jezyk is None:
        warnings.warn(
            f"[SGSPR1] Dla artykulu {artykul.tytul} brak okreslenia jezyka, wybieram polski"
        )
        jezyk = Jezyk.objects.get_or_create(skrot="pol.", nazwa="polski")

    strony = f"{artykul.strona_od}-{artykul.strona_do}"
    if strony == "-":
        strony = None

    konferencja = None
    if artykul.konferencja:
        konferencja = Konferencja.objects.get_or_create(
            nazwa=artykul.konferencja,
            defaults=dict(
                rozpoczecie=artykul.conf_from,
                zakonczenie=artykul.conf_to,
                miasto=artykul.miejscowosc,
                panstwo=artykul.kraj,
                baza_scopus=artykul.scopus or False,
                baza_wos=artykul.wos or False,
            ),
        )[0]

    pbn_id = None
    if artykul.publicationid:
        if artykul.publicationid.startswith("PBN-R:"):
            pbn_id = artykul.publicationid.split(":")[1]
        else:
            adnotacje += f"Publication ID: {artykul.publicationid}\n"

    # Niektóre rekordy mają w tytule rok na początku; są to raczej rozdziały...
    if re.match("\\d\\d\\d\\d ", artykul.tytul[:5]):
        warnings.warn(
            f"[SGSP27] Artykuł {artykul} ma na początku tytułu coś, co wygląda jak rok... obetnę to i wstawię jako "
            f"faktyczny rok publikacji zamiast {artykul.rok_publikacji}."
        )
        artykul.rok_publikacji = int(artykul.tytul[:5].strip())
        artykul.tytul = artykul.tytul[5:].strip()

    args = {
        "id": artykul.id,
        "punkty_kbn": artykul.pkt or 0,
        "tytul_oryginalny": artykul.tytul.strip(),
        "tytul": artykul.title,
        "jezyk": jezyk,
        "rok": artykul.rok_publikacji,
        "tom": artykul.volume,
        "strony": strony,
        "doi": artykul.doi,
        "konferencja": konferencja,
        "public_www": artykul.url,
        "issn": artykul.issn,
        "pbn_id": pbn_id,
    }

    if artykul.kind is None:
        # jeden jedyny artykuł ma kind = None i ma ID = 1
        # jeżeli jakikolwiek inny ma to zgłąszaj błąd
        if artykul.id == 1:
            return
        raise NotImplementedError

    if artykul.arkusze:
        args["liczba_znakow_wydawniczych"] = artykul.arkusze * ILOSC_ZNAKOW_NA_ARKUSZ

        if args["liczba_znakow_wydawniczych"] > (1 << 31):
            warnings.warn(
                f"[SGSP23] Liczba znaków wydawniczych dla rekordu {artykul} wychodzi astronomicznie"
                f" wysoka (większa od {1<<31} i nie może być przechowywana po stronie BPP. Użyję oryginalnej"
                f" wartości czyli {artykul.arkusze} "
            )
            args["liczba_znakow_wydawniczych"] = artykul.arkusze

    Base_Class = Wydawnictwo_Zwarte
    if artykul.kind == "artykuł":
        Base_Class = Wydawnictwo_Ciagle
        args["charakter_formalny"] = Charakter_Formalny.objects.get(skrot="AC")

        if artykul.parent_id is None:
            if artykul.issn is None:
                raise ValueError(f"Brak źródła dla artykułu {artykul}, ISSN też pusty")

        try:
            if artykul.parent_id is not None:
                args["zrodlo"] = Zrodlo.objects.get(issn=artykul.parent_id)
            else:
                args["zrodlo"] = Zrodlo.objects.get(issn=artykul.issn)
        except Zrodlo.DoesNotExist:
            warnings.warn(
                f"[SGSP01] Brak źródła o ISSN {artykul.parent_id} oraz {artykul.issn} dla {artykul}, "
                f"nie zostanie on zaimportowany, ponieważ po stronie BPP artykuł *musi* mieć określone "
                f"źródło."
            )
            return

    else:
        Base_Class = Wydawnictwo_Zwarte
        if artykul.kind == "książka":
            args["charakter_formalny"] = Charakter_Formalny.objects.get(skrot="KS")
            args["isbn"] = artykul.isbn
        elif artykul.kind == "rozdział":
            args["charakter_formalny"] = Charakter_Formalny.objects.get(skrot="ROZ")
            if artykul.isbn:
                args["isbn"] = artykul.isbn
        else:
            raise NotImplementedError(
                f"Nie obsługuję rodzaju {artykul.kind}, rekord {artykul}"
            )

        if artykul.miejsce_wydania is not None:
            args[
                "miejsce_i_rok"
            ] = f"{artykul.miejsce_wydania} {artykul.rok_publikacji}"

        if artykul.wydawca:
            artykul_wydawca = artykul.wydawca
            if artykul_wydawca == "huhu":
                if artykul.parent_id is not None and artykul.parent_id.startswith(
                    "PBN-R:"
                ):
                    artykul_nadrzedny = None

                    try:
                        rodzic = SGSP_Artykul.objects.get(
                            publicationid=artykul.parent_id
                        )
                    except SGSP_Artykul.DoesNotExist:
                        warnings.warn(
                            f"[SGSP23] Brak wydawnictwa zwartego o ID PBN: {artykul.parent_id[6:]} dla rekordu "
                            f"{artykul}, a jest ono rodzicem tego rekordu. Rekord zostanie zaimportowany, ale "
                            f"prawdopodobnie BEZ prawidłowego WYDAWCY!"
                        )
                        rodzic = None

                    if rodzic is not None:
                        artykul_nadrzedny = importuj_pojedynczy_artykul(rodzic)

                    if artykul_nadrzedny is None:
                        warnings.warn(
                            f"[SGSP22] Dla rekordu {artykul} wydawca to {artykul.wydawca}, zatem zostanie"
                            f" użyty wydawca z pola PARENT ID czyli {artykul.parent_id}, ale parent ID "
                            f" wychodzi NONE, rekord zostanie zaimportowany, ale prawdopodobnie BEZ prawidłowego "
                            f"wydawcy!"
                        )
                    else:
                        if artykul_nadrzedny.wydawca_id:
                            args["wydawca"] = artykul_nadrzedny.wydawca
                            args["wydawca_opis"] = artykul_nadrzedny.wydawca_opis

                        elif artykul_nadrzedny.wydawca_opis:
                            args["wydawca_opis"] = artykul_nadrzedny.wydawca_opis

                        else:
                            warnings.warn(
                                f"[SGSP21] Dla rekordu {artykul} wydawca to {artykul.wydawca}, zatem zostanie"
                                f" użyty wydawca z pola PARENT ID czyli {artykul.parent_id}, ale parent nie ma "
                                f"wydawcy badz wydawcy + opisu... rekord NIE zostanie zaimportowany!"
                            )
                            return
                else:
                    if artykul.parent_id is not None:
                        warnings.warn(
                            f"[SGSP20] Dla rekordu {artykul} wydawca to {artykul.wydawca}, zatem zostanie"
                            f" użyty wydawca z pola PARENT ID czyli {artykul.parent_id}"
                        )

                        artykul_wydawca = artykul.parent_id

            if artykul_wydawca != "huhu":
                wydawca = matchuj_wydawce(artykul_wydawca)
                if wydawca:
                    args["wydawca"] = wydawca
                else:
                    args["wydawca_opis"] = artykul_wydawca

            else:
                warnings.warn(
                    f"[SGSP24] dla rekordu {artykul} wydawca to {artykul.wydawca} i nie udało się ustalić"
                    f" żadnej rozsądnej wartości; sprawdź, czy rekord jest zaimportowany z dobrym wydawcą. "
                )

    if artykul.parenttitle is not None:
        artykul.szczegoly = "W: " + artykul.parenttitle

    if artykul.parent_id is not None:
        if re.match("\\d\\d\\d\\d-\\d\\d\\d(\\d|X)", artykul.parent_id):
            if Base_Class != Wydawnictwo_Ciagle:
                warnings.warn(
                    f"[SGSP02] Rozdział/książka, ale z rodzicem w ISSN, funkcja nie obsługiwana... {artykul}. "
                    f"Rekord nie zostanie zaimportowany"
                )
                return

            try:
                args["zrodlo"] = Zrodlo.objects.get(issn=artykul.parent_id)
            except Zrodlo.DoesNotExist:
                warnings.warn(
                    f"[SGSP03] Brak źródła o ISSN {artykul.parent_id} dla {artykul}, nie zostanie on zaimportowany"
                )
                return

        elif artykul.parent_id.startswith("PBN-R:"):
            if Base_Class != Wydawnictwo_Zwarte:
                raise NotImplementedError(
                    f"Artykuł, ale z rodzicem PBN-ID, funkcja nie obsługiwana... {artykul}"
                )
            try:
                args["wydawnictwo_nadrzedne"] = Wydawnictwo_Zwarte.objects.get(
                    pbn_id=artykul.parent_id[6:]
                )
            except Wydawnictwo_Zwarte.DoesNotExist:
                try:
                    rodzic = SGSP_Artykul.objects.get(publicationid=artykul.parent_id)
                except SGSP_Artykul.DoesNotExist:
                    warnings.warn(
                        f"[SGSP04] Brak wydawnictwa zwartego o ID PBN: {artykul.parent_id[6:]} dla rekordu {artykul},"
                        f" a jest ono rodzicem tego rekordu. Rekord ZOSTANIE zaimportowany, ale bez prawidłowego "
                        f"wydawnictwa nadrzędnego!!!"
                    )
                    args["wydawnictwo_nadrzedne"] = None
                else:
                    args["wydawnictwo_nadrzedne"] = importuj_pojedynczy_artykul(rodzic)

        elif (
            (artykul.parent_id == artykul.wydawca)
            or (artykul.parent_id.find(artykul.wydawca) >= 0)
            or (artykul.wydawca.find(artykul.parent_id) >= 0)
            or (artykul.parent_id.startswith(artykul.wydawca))
            or (artykul.wydawca.startswith(artykul.parent_id))
            or (
                artykul.parent_id == "CNBOP-PIB"
                and artykul.wydawca
                == "Centrum Naukowo-Badawcze Ochrony Przeciwpożarowejim. Józefa Tuliszkowskiego – "
                "Państwowy Instytut Badawczy"
            )
            or (
                artykul.parent_id
                == "Centrum Naukowo-Badawcze Ochrony Przeciwpożarowej im. Józefa Tuliszkowskiego "
                "Państwowy Instytut Badawczy"
                and artykul.wydawca
                == "Centrum Naukowo Badawcze-Badawcze Ochrony Przeciwpożarowej im. Józefa Tuliszkowskiego - "
                "Państwowy Instytut Badawczy"
            )
            or (
                artykul.parent_id == "GRUPA MEDIUM"
                and artykul.wydawca == "Dom Wydawniczy MEDIUM"
            )
            or (
                artykul.parent_id == "OWPW"
                and artykul.wydawca.find("Oficyna Wydawnicza PW") >= 0
            )
            or (
                artykul.parent_id == "SGSP"
                and artykul.wydawca == "Szkoła Główna Służby Pożarniczej"
            )
            or artykul.parent_id == "SP PSP Bydgoszcz"
        ):
            if args.get("wydawca", None) or args.get("wydawca_opis", None):
                # jest OK, parent_id jest dziwny, ale identyczny lub prawie-identyczny jak wydawca, a wydawca
                # już został ustalony, więc nie trzeba krzyczeć.
                pass
            else:
                warnings.warn(
                    f'[SGSP05] Nie wiem co zrobic z rodzicem "{artykul.parent_id}" artykulu {artykul}. '
                    f"Wydawca tego rekordu to {artykul.wydawca}, ale po stronie BPP nie udało się tego "
                    f"wydawcy zmatchować. Rekord zostanie zaimportowany, ale najprawdopodobniej z nieprawidłowym"
                    f" rodzicem rekordu bądź wydawcą "
                )

        else:
            warnings.warn(
                f'[SGSP05] Nie wiem co zrobic z rodzicem "{artykul.parent_id}" artykulu {artykul}. Wydawca'
                f" dla tego rekordu to {artykul.wydawca}. Rekord zostanie zaimportowany ale prawdopodobnie "
                f"ze złym rekordem nadrzędnym bądź niepoprawnym wydawcą. Do weryfikacji! "
            )

    args["status_korekty"] = Status_Korekty.objects.get(nazwa="przed korektą")
    args["typ_kbn"] = Typ_KBN.objects.get(nazwa="inne")

    if (
        args["pbn_id"] is not None
        and Base_Class.objects.filter(pbn_id=args["pbn_id"]).exists()
    ):
        warnings.warn(
            f"[SGSP25] Rekord {artykul} nie zostanie zaimportowany, bo są już rekordy z identycznym PBN ID"
            f" {args['pbn_id']}. "
        )
        return

    if artykul.kind == "rozdział" and args.get("wydawnictwo_nadrzedne", None) is None:
        warnings.warn(
            f"[SGSP27] Artykuł {artykul} to rozdział bez ustalonego wydawnictwa nadrzędnego. Prawdopodobnie po "
            f"zaimportowaniu go po stronie będzie niepoprawnie!"
        )

    try:
        rekord = Base_Class.objects.create(**args)
    except IntegrityError as e:
        warnings.warn(
            f"[SGSP06] Rekord {artykul} nie został zaimportowany; przyczyna {e}"
        )
        return
    except DataError as e:
        warnings.warn(
            f"[SGSP07] Rekord {artykul} nie został zaimportowany; przyczyna {e}"
        )
        return

    rekord: Wydawnictwo_Zwarte | Wydawnictwo_Ciagle

    if artykul.abstrakt:
        rekord.streszczenia.create(
            jezyk_streszczenia=rekord.jezyk, streszczenie=artykul.abstrakt
        )

    return rekord


def import_artykuly():
    artykul: SGSP_Artykul
    for artykul in SGSP_Artykul.objects.all():
        importuj_pojedynczy_artykul(artykul)


def patch_database():
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute(
        "UPDATE cuvier_artykuly SET conf_to = '2013-06-26' where conf_to = '62016-06-26'"
    )
    cursor.execute("UPDATE cuvier_artykuly SET arkusze = 0-arkusze where arkusze < 0")
    cursor.execute("DELETE FROM cuvier_artykuly WHERE id = 1")


def install_uczelnia():
    uczelnia = Uczelnia.objects.get_or_create(
        nazwa="Szkoła Główna Służby Pożarniczej", skrot="SGSP"
    )[0]

    obca_jednostka = Jednostka.objects.get_or_create(
        nazwa="Obca jednostka",
        skrot="Obc. jedn.",
        uczelnia=uczelnia,
        skupia_pracownikow=False,
    )[0]
    uczelnia.obca_jednostka = obca_jednostka
    uczelnia.save()

    wydzial = Wydzial.objects.get_or_create(
        nazwa="Wydział domyślny SGSP", skrot="WdSGSP", uczelnia=uczelnia
    )[0]

    Jednostka.objects.get_or_create(
        nazwa=JEDNOSTKA_DOMYSLNA_SGSP,
        skrot="Jedn. dom. SGSP",
        uczelnia=uczelnia,
        wydzial=wydzial,
    )

    return uczelnia, wydzial


def import_pojedynczy_autor(autor_artykulu: SGSP_Artykul_Autor):
    rekord = znajdz_rekord_po_stronie_bpp(autor_artykulu.artykul_id)
    if rekord is None:
        obcy = ""
        if autor_artykulu.obcy:
            obcy = "OBCY"

        warnings.warn(
            f"[SGSP08] W bazie BPP nie utworzono odpowiednika dla artykułu o ID {autor_artykulu.artykul_id}, "
            f"autorzy nie mogą zostać zaimportowani. Chciałem zaimportować autora tego artykułu o ID {obcy} "
            f"{autor_artykulu.autor_id}. "
        )
        return

    skrot = "aut."
    if autor_artykulu.jest_redaktorem:
        skrot = "red."

    typ_odpowiedzialnosci = Typ_Odpowiedzialnosci.objects.get(skrot=skrot)

    # Znajdźmy autora. Autor obcy trzymany jest w oddzielnej tabeli.
    if autor_artykulu.obcy:
        try:
            autor = Autor.objects.get(
                id=autor_artykulu.autor_id + OBCY_AUTORZY_ID_START
            )
        except Autor.DoesNotExist:
            try:
                obcy_autor_sgsp = SGSP_Obcy_Autor.objects.get(
                    pk=autor_artykulu.autor_id
                )
            except SGSP_Obcy_Autor.DoesNotExist:
                warnings.warn(
                    f"[SGSP18] Brak w bazie SGSP OBCEGO autora o ID {autor_artykulu.autor_id}. "
                    f"Autor wymagany jest dla rekordu {autor_artykulu.artykul}. Autor nie zostanie dopisany!"
                )
                return

            try:
                nazwisko, imiona = obcy_autor_sgsp.name.split(" ")
            except ValueError:
                nazwisko, imiona = obcy_autor_sgsp.name, ""

            autor = Autor.objects.get_or_create(
                pk=autor_artykulu.autor_id + OBCY_AUTORZY_ID_START,
                nazwisko=nazwisko,
                imiona=imiona,
            )[0]
            autor.autor_jednostka_set.get_or_create(
                jednostka=Uczelnia.objects.first().obca_jednostka
            )
    else:
        # not autor_artykulu.obcy

        if autor_artykulu.autor_id is None:
            warnings.warn(
                f"[SGSP26] Dla artykułu {autor_artykulu.artykul} podany jest autor o pustym ID. "
                f"Nie można zaimportować takiej informacji. Sprawdź autorów po stronie SGSP lub "
                f"po imporcie dla tego artykułu. "
            )
            return

        try:
            autor = Autor.objects.get(id=autor_artykulu.autor_id)
        except Autor.DoesNotExist:
            if autor_artykulu.obcy:
                raise NotImplementedError("To nie powinno nastąpić")

            try:
                warnings.warn(
                    f"[SGSP09] Dla artykulu {autor_artykulu.artykul} podany jest autor o ID "
                    f"{autor_artykulu.autor_id}, ale nie ma go po stronie BPP. Autor: {autor_artykulu.autor}. "
                    f"Autor nie zostanie dodany do rekordu!"
                )
                return

            except SGSP_Pracownik.DoesNotExist:
                warnings.warn(
                    f"[SGSP10] Dla artykulu {autor_artykulu.artykul} podany jest autor o ID "
                    f"{autor_artykulu.autor_id}, "
                    f"ale nie ma go po stronie BPP ani po stronie SGSP. Autor nie zosanie dodany "
                    f"do rekordu!"
                )
                return

    # Ile autor ma jednostek?
    cnt = autor.autor_jednostka_set.count()

    afiliuje = autor_artykulu.afiliacja == "SGSP"

    if autor_artykulu.obcy:
        if cnt > 1:
            warnings.warn(
                f"[SGSP11] Autor {autor} artykulu {autor_artykulu.artykul} jest OBCY, ale ma ponad jedną "
                f"jednostkę przypisaną w systemie. Używam obcej jednostki."
            )
        jednostka = Uczelnia.objects.first().obca_jednostka

        if afiliuje:
            warnings.warn(
                f"[SGSP12] Autor {autor} artykulu {autor_artykulu.artykul} jest OBCY, mimo to ma ustawioną afiliację"
                f"na SGSP, ustawialm afiliuje na FALSE, gdyż taki rekord nie mógłby zostac zaimportowany do BPP. "
                f"Rekordy obcych autorów muszą mieć wartość afiliuje równą FALSE"
            )
            afiliuje = False

    elif cnt == 0:
        warnings.warn(
            f"[SGSP13] Dla autora {autor} w pracy {autor_artykulu.artykul} nie można ustalić jednostki, gdyż "
            f"ten autor nie ma po stronie BPP przypisanej żadnej jednostki. "
            f"Zostanie przydzielona jednostka domyślna (systemowa). "
        )
        jednostka = Jednostka.objects.get(nazwa=JEDNOSTKA_DOMYSLNA_SGSP)
    elif cnt == 1:
        jednostka = autor.autor_jednostka_set.first().jednostka
    else:
        # Autor ma przypisane 2 lub więcej jednostek; którą przypisać do pracy?
        pierwsza_nieobca_jednostka = autor.autor_jednostka_set.filter(
            jednostka__skupia_pracownikow=True
        ).first()

        if pierwsza_nieobca_jednostka is not None:
            # Autor ma więcej, niż jedną jednostkę; znaleziono pierwszą nie-obcą jednostkę. Jeżeli autor ma
            # przypisane 2 jednostki (obca, nie-obca) to OK. Jeżeli ma więcej, niż jedną, to wyemituj
            # ostrzeżenie:
            if cnt > 2:
                warnings.warn(
                    f"[SGSP14] Autor {autor} artykulu {autor_artykulu.artykul} ma wiecej niz jedna jednostke, "
                    f"uzywam pierwszej nie-obcej czyli {pierwsza_nieobca_jednostka}"
                )
        else:
            lista_jednostek = list(
                autor.autor_jednostka_set.values_list("jednostka__nazwa", flat=True)
            )
            raise NotImplementedError(
                "[SGSP15] Autor ma przypisania w systemie 2 lub więcej jednostek, ale nie-obca "
                f"jednostka w jego wykazie nie istnieje. Jednostki autora: {lista_jednostek}"
            )

        jednostka = pierwsza_nieobca_jednostka.jednostka

    rekord: Wydawnictwo_Zwarte | Wydawnictwo_Ciagle

    if rekord.autorzy_set.filter(
        autor=autor, typ_odpowiedzialnosci=typ_odpowiedzialnosci
    ).exists():
        warnings.warn(
            f"[SGSP16] W rekordzie {autor_artykulu.artykul} autor {autor} jest już raz przypisany, "
            f"z typem odpowiedzialności {typ_odpowiedzialnosci}. Nie przypisuję ponownie. "
        )
        return

    kolejnosc = autor_artykulu.kolejnosc
    while True:
        warning_emited = False
        if rekord.autorzy_set.filter(kolejnosc=kolejnosc).exists():
            if not warning_emited:
                warnings.warn(
                    f"[SGSP17] W rekordzie {autor_artykulu.artykul} autor {autor} jest przypisany "
                    f"z kolejnością {kolejnosc}, ale okazuje się, że jest już autor z taką kolejnością. "
                    f"Zatem przypiszę mu następny numer w kolejnosci. Sprawdź kolejność autorów tego rekordu"
                    f" po imporcie!"
                )
                warning_emited = True
            kolejnosc += 1
        else:
            break

    rekord.autorzy_set.get_or_create(
        autor=autor,
        kolejnosc=kolejnosc,
        afiliuje=afiliuje,
        typ_odpowiedzialnosci=typ_odpowiedzialnosci,
        jednostka=jednostka,
        zapisany_jako=f"{autor.nazwisko} {autor.imiona}".strip(),
    )


def import_artykuly_autorzy():
    for autor_artykulu in SGSP_Artykul_Autor.objects.all():
        import_pojedynczy_autor(autor_artykulu)


def import_sgsp_db():
    patch_database()

    import_journals()

    uczelnia, wydzial = install_uczelnia()
    import_komorki(uczelnia=uczelnia, wydzial=wydzial)

    Autor.objects.all().delete()
    import_users()

    Wydawnictwo_Ciagle.objects.all().delete()
    Wydawnictwo_Zwarte.objects.all().delete()
    import_artykuly()

    Wydawnictwo_Ciagle_Autor.objects.all().delete()
    Wydawnictwo_Zwarte_Autor.objects.all().delete()
    import_artykuly_autorzy()

    print(
        "Don't forget to execute:\n\t"
        "bpp-manage.py sqlsequencereset bpp|grep -v zewnetrzne_bazy_view|grep -v temporary_cpaq|"
        "grep -v bpp_nowe_sumy_view|psql bpp\n\t"
        "echo DELETE FROM denorm_dirtyinstance | psql bpp\n\t"
        "bpp-manage.py denorm_rebuild\n\t"
        "bpp-manage.py createsuperuser --username admin"
    )
