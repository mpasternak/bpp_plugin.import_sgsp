--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4
--
-- SET statement_timeout = 0;
-- SET lock_timeout = 0;
-- SET idle_in_transaction_session_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SELECT pg_catalog.set_config('search_path', '', false);
-- SET check_function_bodies = false;
-- SET xmloption = content;
-- SET client_min_messages = warning;
-- SET row_security = off;
--
-- SET default_tablespace = '';
--
-- SET default_table_access_method = heap;
--

--
-- Name: update_modified_column(); Type: FUNCTION; Schema: public; Owner: mimooh
--

CREATE OR REPLACE FUNCTION update_modified_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.modified = now();
    RETURN NEW;
END;
$$;

--
-- Name: cuvier_artykul_autor; Type: TABLE; Schema: public; Owner: mimooh
--

DROP TABLE IF EXISTS cuvier_artykul_autor;

CREATE TABLE cuvier_artykul_autor (
    id integer NOT NULL,
    id_artykulu integer,
    id_autora integer,
    kolejnosc integer,
    obcy integer,
    afiliacja text,
    modifier text,
    modified date DEFAULT now() NOT NULL,
    jest_redaktorem integer,
    pbnart text,
    pbnauthor text,
    ostatni_edytor text,
    dyscyplina text,
    d_kandydat1 text,
    d_kandydat2 text,
    d_kandydat3 text,
    oswiadczenie numeric,
    content_type_id integer,
    object_id integer
);



--
-- Name: cuvier_artykul_autor_id_seq; Type: SEQUENCE; Schema: public; Owner: mimooh
--

CREATE SEQUENCE IF NOT EXISTS cuvier_artykul_autor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cuvier_artykul_autor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mimooh
--

ALTER SEQUENCE cuvier_artykul_autor_id_seq OWNED BY cuvier_artykul_autor.id;


--
-- Name: cuvier_artykuly; Type: TABLE; Schema: public; Owner: mimooh
--
DROP TABLE IF EXISTS cuvier_artykuly;

CREATE TABLE IF NOT EXISTS cuvier_artykuly (
    id integer NOT NULL,
    tytul text,
    jezyk text,
    rok_publikacji integer,
    wersja text,
    volume text,
    issue text,
    strona_od integer,
    strona_do integer,
    licencja text,
    doi text,
    uswiecony text,
    issn text,
    abstrakt text,
    konferencja text,
    scopus text,
    wos text,
    conf_from date,
    conf_to date,
    kraj text,
    file text,
    modifier integer,
    title text,
    arkusze integer,
    othercontributors integer,
    kind text,
    isbn text,
    publicationid text,
    parentid text,
    parenttitle text,
    wydawca text,
    miejsce_wydania text,
    wydanie text,
    sygnatura text,
    url text,
    miejscowosc text,
    ostatni_edytor text,
    modified timestamp without time zone DEFAULT now() NOT NULL,
    pkt integer,
    force_pkt integer,
    content_type_id integer,
    object_id integer
);


--
-- Name: cuvier_artykuly_id_seq; Type: SEQUENCE; Schema: public; Owner: mimooh
--

CREATE SEQUENCE IF NOT EXISTS cuvier_artykuly_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cuvier_artykuly_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mimooh
--

ALTER SEQUENCE cuvier_artykuly_id_seq OWNED BY cuvier_artykuly.id;


--
-- Name: cuvier_in_pbn; Type: TABLE; Schema: public; Owner: mimooh
--

DROP TABLE IF EXISTS cuvier_in_pbn;

CREATE TABLE IF NOT EXISTS cuvier_in_pbn (
    id integer NOT NULL,
    id_artykulu integer,
    pbn_id_artykulu text,
    date date,
    status text
);



--
-- Name: cuvier_in_pbn_id_seq; Type: SEQUENCE; Schema: public; Owner: mimooh
--

CREATE SEQUENCE IF NOT EXISTS cuvier_in_pbn_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cuvier_in_pbn_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mimooh
--

ALTER SEQUENCE cuvier_in_pbn_id_seq OWNED BY cuvier_in_pbn.id;


--
-- Name: cuvier_journals; Type: TABLE; Schema: public; Owner: mimooh
--

DROP TABLE IF EXISTS cuvier_journals;

CREATE TABLE IF NOT EXISTS cuvier_journals (
    issn text,
    journal text,
    ostatni_edytor text,
    modified timestamp without time zone DEFAULT now() NOT NULL,
    bpp_zrodlo_id integer
);



--
-- Name: cuvier_journals_pkt; Type: TABLE; Schema: public; Owner: mimooh
--
DROP TABLE IF EXISTS cuvier_journals_pkt;

CREATE TABLE IF NOT EXISTS cuvier_journals_pkt (
    id integer NOT NULL,
    issn text,
    rok integer,
    pkt integer,
    ostatni_edytor text,
    modified timestamp without time zone DEFAULT now() NOT NULL
);



--
-- Name: cuvier_komorki; Type: TABLE; Schema: public; Owner: mimooh
--
DROP TABLE IF EXISTS cuvier_komorki;

CREATE TABLE IF NOT EXISTS cuvier_komorki (
    id text NOT NULL,
    nazwa text,
    alias text,
    ostatni_edytor text,
    modified timestamp without time zone DEFAULT now() NOT NULL,
    sciezka text,
    usos text,
    kdydaktyczna integer,
    bpp_jednostka_id integer
);



--
-- Name: cuvier_liczba_n; Type: TABLE; Schema: public; Owner: mimooh
--

DROP TABLE IF EXISTS cuvier_liczba_n;

CREATE TABLE IF NOT EXISTS cuvier_liczba_n (
    id integer NOT NULL,
    wykladowca_id integer,
    y2017 numeric,
    y2018 numeric,
    y2019 numeric,
    y2020 numeric,
    y2021 numeric,
    n_od integer,
    dyscyplina text,
    ybonus numeric,
    d integer,
    n4 numeric
);



--
-- Name: cuvier_liczba_n_id_seq; Type: SEQUENCE; Schema: public; Owner: mimooh
--

CREATE SEQUENCE IF NOT EXISTS cuvier_liczba_n_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cuvier_liczba_n_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mimooh
--

ALTER SEQUENCE cuvier_liczba_n_id_seq OWNED BY cuvier_liczba_n.id;


--
-- Name: cuvier_o; Type: TABLE; Schema: public; Owner: mimooh
--
DROP TABLE IF EXISTS cuvier_o;

CREATE TABLE IF NOT EXISTS cuvier_o (
    id integer NOT NULL,
    data text,
    autor text,
    conf text,
    artykulow integer,
    wynik numeric,
    dyscyplina text,
    comment text,
    ostatni_edytor text,
    modified timestamp without time zone DEFAULT now() NOT NULL
);



--
-- Name: cuvier_o_id_seq; Type: SEQUENCE; Schema: public; Owner: mimooh
--

CREATE SEQUENCE IF NOT EXISTS cuvier_o_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cuvier_o_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mimooh
--

ALTER SEQUENCE cuvier_o_id_seq OWNED BY cuvier_o.id;


--
-- Name: cuvier_obcy_autorzy; Type: TABLE; Schema: public; Owner: mimooh
--
DROP TABLE IF EXISTS cuvier_obcy_autorzy;

CREATE TABLE IF NOT EXISTS cuvier_obcy_autorzy (
    id integer NOT NULL,
    name text,
    ostatni_edytor text,
    modified timestamp without time zone DEFAULT now() NOT NULL,
    bpp_autor_id integer
);



--
-- Name: cuvier_obcy_autorzy_id_seq; Type: SEQUENCE; Schema: public; Owner: mimooh
--

CREATE SEQUENCE IF NOT EXISTS cuvier_obcy_autorzy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cuvier_obcy_autorzy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mimooh
--

ALTER SEQUENCE cuvier_obcy_autorzy_id_seq OWNED BY cuvier_obcy_autorzy.id;


--
-- Name: cuvier_pracownicy; Type: TABLE; Schema: public; Owner: mimooh
--
DROP TABLE IF EXISTS cuvier_pracownicy;

CREATE TABLE IF NOT EXISTS cuvier_pracownicy (
    id integer NOT NULL,
    imie character varying(100),
    nazwisko character varying(100),
    telefon text,
    email text,
    komorka text,
    stopien text,
    tytul text,
    pensum_nowe integer,
    stanowisko text,
    konsultacje text,
    modified timestamp without time zone DEFAULT now(),
    dydaktyk integer,
    adijoz_admin integer,
    godzinek_admin integer,
    pracownicy_admin integer,
    ramowy_admin integer,
    name text,
    master_admin integer,
    cuvier_admin integer,
    zatrudniony_od date,
    zatrudniony_do date,
    ipos_id integer,
    orcid text,
    wyksztalcenie text,
    rok_stopien date,
    rok_tytul date,
    pbnauthor text,
    fet_admin integer,
    simple_id integer,
    dziekanat_admin integer,
    pierwsze_mp integer,
    nowe_nazwisko text,
    nowe_nazwisko_data date,
    ostatni_edytor text,
    short text,
    pensum_stare integer,
    stanowisko_adm text,
    badawcze text,
    asos_accept integer,
    instytut text,
    forma_zatrudnienia text,
    przetwarzany integer,
    email_sgsp text,
    sciezka text,
    struktura_admin integer,
    funkcja_id integer,
    hero_admin integer,
    budzet_admin text,
    promotor integer,
    name_postfix text,
    komorka_adijoz text,
    komorka_dydaktyk text,
    pokoj text,
    plec text,
    usos_id integer,
    ankieta_ocena_srednia numeric,
    ankieta_ocena_cykl text,
    pasjans_admin integer,
    tryb_pracy text,
    stanowisko_adm2 text,
    profil_www text,
    adijoz_planeta integer,
    default_cdyd_kod text,
    planetarny integer,
    srs_admin integer,
    rozliczenia_admin integer,
    bpp_autor_id integer
);


--
-- Name: journals_pkt_id_seq; Type: SEQUENCE; Schema: public; Owner: mimooh
--

CREATE SEQUENCE IF NOT EXISTS journals_pkt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: journals_pkt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mimooh
--

ALTER SEQUENCE journals_pkt_id_seq OWNED BY cuvier_journals_pkt.id;


--
-- Name: pracownicy_id_seq; Type: SEQUENCE; Schema: public; Owner: mimooh
--

CREATE SEQUENCE IF NOT EXISTS pracownicy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pracownicy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mimooh
--

ALTER SEQUENCE pracownicy_id_seq OWNED BY cuvier_pracownicy.id;


--
-- Name: cuvier_artykul_autor id; Type: DEFAULT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_artykul_autor ALTER COLUMN id SET DEFAULT nextval('cuvier_artykul_autor_id_seq'::regclass);


--
-- Name: cuvier_artykuly id; Type: DEFAULT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_artykuly ALTER COLUMN id SET DEFAULT nextval('cuvier_artykuly_id_seq'::regclass);


--
-- Name: cuvier_in_pbn id; Type: DEFAULT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_in_pbn ALTER COLUMN id SET DEFAULT nextval('cuvier_in_pbn_id_seq'::regclass);


--
-- Name: cuvier_journals_pkt id; Type: DEFAULT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_journals_pkt ALTER COLUMN id SET DEFAULT nextval('journals_pkt_id_seq'::regclass);


--
-- Name: cuvier_liczba_n id; Type: DEFAULT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_liczba_n ALTER COLUMN id SET DEFAULT nextval('cuvier_liczba_n_id_seq'::regclass);


--
-- Name: cuvier_o id; Type: DEFAULT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_o ALTER COLUMN id SET DEFAULT nextval('cuvier_o_id_seq'::regclass);


--
-- Name: cuvier_obcy_autorzy id; Type: DEFAULT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_obcy_autorzy ALTER COLUMN id SET DEFAULT nextval('cuvier_obcy_autorzy_id_seq'::regclass);


--
-- Name: cuvier_pracownicy id; Type: DEFAULT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_pracownicy ALTER COLUMN id SET DEFAULT nextval('pracownicy_id_seq'::regclass);


--
-- Name: cuvier_artykul_autor cuvier_artykul_autor_pkey; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_artykul_autor
    ADD CONSTRAINT cuvier_artykul_autor_pkey PRIMARY KEY (id);


--
-- Name: cuvier_artykuly cuvier_artykuly_pkey; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_artykuly
    ADD CONSTRAINT cuvier_artykuly_pkey PRIMARY KEY (id);


--
-- Name: cuvier_in_pbn cuvier_in_pbn_pkey; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_in_pbn
    ADD CONSTRAINT cuvier_in_pbn_pkey PRIMARY KEY (id);


--
-- Name: cuvier_liczba_n cuvier_liczba_n_pkey; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_liczba_n
    ADD CONSTRAINT cuvier_liczba_n_pkey PRIMARY KEY (id);


--
-- Name: cuvier_o cuvier_o_pkey; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_o
    ADD CONSTRAINT cuvier_o_pkey PRIMARY KEY (id);


--
-- Name: cuvier_obcy_autorzy cuvier_obcy_autorzy_pkey; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_obcy_autorzy
    ADD CONSTRAINT cuvier_obcy_autorzy_pkey PRIMARY KEY (id);


--
-- Name: cuvier_journals_pkt journals_pkt_pkey; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_journals_pkt
    ADD CONSTRAINT journals_pkt_pkey PRIMARY KEY (id);


--
-- Name: cuvier_komorki komorki_pkey; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_komorki
    ADD CONSTRAINT komorki_pkey PRIMARY KEY (id);


--
-- Name: cuvier_pracownicy pracownicy_nazwisko_imie_key; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_pracownicy
    ADD CONSTRAINT pracownicy_nazwisko_imie_key UNIQUE (nazwisko, imie);


--
-- Name: cuvier_pracownicy pracownicy_pkey; Type: CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_pracownicy
    ADD CONSTRAINT pracownicy_pkey PRIMARY KEY (id);


--
-- Name: idx_cuvier_jp_issn; Type: INDEX; Schema: public; Owner: mimooh
--

CREATE INDEX idx_cuvier_jp_issn ON cuvier_journals_pkt USING btree (issn);


--
-- Name: idx_cuvier_jp_pkt; Type: INDEX; Schema: public; Owner: mimooh
--

CREATE INDEX idx_cuvier_jp_pkt ON cuvier_journals_pkt USING btree (pkt);


--
-- Name: idx_cuvier_jp_rok; Type: INDEX; Schema: public; Owner: mimooh
--

CREATE INDEX idx_cuvier_jp_rok ON cuvier_journals_pkt USING btree (rok);


--
-- Name: journal_issn; Type: INDEX; Schema: public; Owner: mimooh
--

CREATE UNIQUE INDEX journal_issn ON cuvier_journals USING btree (issn);


--
-- Name: komorki_id; Type: INDEX; Schema: public; Owner: mimooh
--

CREATE UNIQUE INDEX komorki_id ON cuvier_komorki USING btree (id);


--
-- Name: pracownicy_name; Type: INDEX; Schema: public; Owner: mimooh
--

CREATE UNIQUE INDEX pracownicy_name ON cuvier_pracownicy USING btree (name);


--
-- Name: cuvier_artykul_autor update_modified; Type: TRIGGER; Schema: public; Owner: mimooh
--

CREATE TRIGGER update_modified BEFORE UPDATE ON cuvier_artykul_autor FOR EACH ROW EXECUTE FUNCTION update_modified_column();


--
-- Name: cuvier_artykuly update_modified; Type: TRIGGER; Schema: public; Owner: mimooh
--

CREATE TRIGGER update_modified BEFORE UPDATE ON cuvier_artykuly FOR EACH ROW EXECUTE FUNCTION update_modified_column();


--
-- Name: cuvier_journals update_modified; Type: TRIGGER; Schema: public; Owner: mimooh
--

CREATE TRIGGER update_modified BEFORE UPDATE ON cuvier_journals FOR EACH ROW EXECUTE FUNCTION update_modified_column();


--
-- Name: cuvier_journals_pkt update_modified; Type: TRIGGER; Schema: public; Owner: mimooh
--

CREATE TRIGGER update_modified BEFORE UPDATE ON cuvier_journals_pkt FOR EACH ROW EXECUTE FUNCTION update_modified_column();


--
-- Name: cuvier_komorki update_modified; Type: TRIGGER; Schema: public; Owner: mimooh
--

CREATE TRIGGER update_modified BEFORE UPDATE ON cuvier_komorki FOR EACH ROW EXECUTE FUNCTION update_modified_column();


--
-- Name: cuvier_obcy_autorzy update_modified; Type: TRIGGER; Schema: public; Owner: mimooh
--

CREATE TRIGGER update_modified BEFORE UPDATE ON cuvier_obcy_autorzy FOR EACH ROW EXECUTE FUNCTION update_modified_column();


--
-- Name: cuvier_pracownicy update_modified; Type: TRIGGER; Schema: public; Owner: mimooh
--

CREATE TRIGGER update_modified BEFORE UPDATE ON cuvier_pracownicy FOR EACH ROW EXECUTE FUNCTION update_modified_column();


--
-- Name: cuvier_artykul_autor cuvier_artykul_autor_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_artykul_autor
    ADD CONSTRAINT cuvier_artykul_autor_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id);


--
-- Name: cuvier_artykuly cuvier_artykuly_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_artykuly
    ADD CONSTRAINT cuvier_artykuly_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id);


--
-- Name: cuvier_journals cuvier_journals_bpp_zrodlo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_journals
    ADD CONSTRAINT cuvier_journals_bpp_zrodlo_id_fkey FOREIGN KEY (bpp_zrodlo_id) REFERENCES bpp_zrodlo(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: cuvier_komorki cuvier_komorki_bpp_jednostka_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_komorki
    ADD CONSTRAINT cuvier_komorki_bpp_jednostka_id_fkey FOREIGN KEY (bpp_jednostka_id) REFERENCES bpp_jednostka(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: cuvier_obcy_autorzy cuvier_obcy_autorzy_bpp_autor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_obcy_autorzy
    ADD CONSTRAINT cuvier_obcy_autorzy_bpp_autor_id_fkey FOREIGN KEY (bpp_autor_id) REFERENCES bpp_autor(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: cuvier_pracownicy cuvier_pracownicy_bpp_autor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mimooh
--

ALTER TABLE ONLY cuvier_pracownicy
    ADD CONSTRAINT cuvier_pracownicy_bpp_autor_id_fkey FOREIGN KEY (bpp_autor_id) REFERENCES bpp_autor(id) ON UPDATE CASCADE ON DELETE SET NULL;



--
-- PostgreSQL database dump complete
--

