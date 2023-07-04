#!/bin/bash

# Skasuj i utwórz bazę BPP
dropdb bpp
createdb bpp

# Uruchom migracje -- utwórz tabele
bpp-manage.py migrate

# Zaciągnij inicjalne dane, repo github.com/iplweb/bpp-assets
bpp-manage.py loaddata ~/Programowanie/bpp-assets/initial_data/bpp.Dyscyplina_Naukowa.yaml.gz
bpp-manage.py loaddata ~/Programowanie/bpp-assets/initial_data/pbn_api.Publisher.yaml.gz
bpp-manage.py loaddata ~/Programowanie/bpp-assets/initial_data/bpp.Wydawca.yaml.gz
bpp-manage.py loaddata ~/Programowanie/bpp-assets/initial_data/bpp.Poziom_Wydawcy.yaml.gz

# Utwórz kopię tabel CIA w BPP
pg_dump cia | psql bpp

# Utwórz konto superużytkownika
bpp-manage.py createsuperuser --username admin

# Utwórz snapshot "czystej" bazy
pg_dump -Fc bpp> clean-bpp-`date +%Y%m%d%H%M%S`.pgdump

# Uruchom import
bpp-manage.py import_sgsp_db &> import_log.txt

# Zresetuj sekwencje
bpp-manage.py sqlsequencereset bpp|grep -v zewnetrzne_bazy_view|grep -v temporary_cpaq|grep -v bpp_nowe_sumy_view|psql bpp

# Usuń dane odbudowy
echo DELETE FROM denorm_dirtyinstance | psql bpp

# Odbuduj bazę
echo -n "Odbudowa denormalizacji, to potrwa... "
bpp-manage.py denorm_rebuild
echo "zrobione."

# Zrób dump bazy po imporcie
pg_dump -Fc bpp > post-import-bpp-`date +%Y%m%d%H%M%S`.pgdump
