BEGIN;

ALTER TABLE IF EXISTS journals
    RENAME TO cuvier_journals;
ALTER TABLE IF EXISTS journals_pkt
    RENAME TO cuvier_journals_pkt;
ALTER TABLE IF EXISTS komorki
    RENAME TO cuvier_komorki;
ALTER TABLE IF EXISTS pracownicy
    RENAME TO cuvier_pracownicy;

ALTER TABLE cuvier_artykul_autor
    ADD COLUMN IF NOT EXISTS content_type_id INT REFERENCES django_content_type (id);
ALTER TABLE cuvier_artykul_autor
    ADD COLUMN IF NOT EXISTS object_id INT;

ALTER TABLE cuvier_artykuly
    ADD COLUMN IF NOT EXISTS content_type_id INT REFERENCES django_content_type (id);
ALTER TABLE cuvier_artykuly
    ADD COLUMN IF NOT EXISTS object_id INT;

ALTER TABLE cuvier_obcy_autorzy
    ADD COLUMN IF NOT EXISTS bpp_autor_id INT REFERENCES bpp_autor (id) ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE cuvier_pracownicy
    ADD COLUMN IF NOT EXISTS bpp_autor_id INT REFERENCES bpp_autor (id) ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE cuvier_komorki
    ADD COLUMN IF NOT EXISTS bpp_jednostka_id INT REFERENCES bpp_jednostka (id) ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE cuvier_journals
    ADD COLUMN bpp_zrodlo_id INT REFERENCES bpp_zrodlo (id) ON DELETE SET NULL ON UPDATE CASCADE;

DROP VIEW IF EXISTS v_adijoz;
DROP VIEW IF EXISTS v_cuvier_artykul_autor;
DROP VIEW IF EXISTS v_cuvier_artykul_autor_inz;
DROP VIEW IF EXISTS v_cuvier_artykul_autor_nauki;
DROP VIEW IF EXISTS v_cuvier_artykuly;
DROP VIEW IF EXISTS v_cuvier_liczba_n;
DROP VIEW IF EXISTS vp;

COMMIT;