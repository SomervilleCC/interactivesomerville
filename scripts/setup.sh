echo OK
echo

export PG_INITSCRIPT=/etc/init.d/postgresql-8.3
export POSTGIS_SQL=/usr/share/postgresql-8.3-postgis/lwpostgis.sql
export SPATIAL_REF_SQL=/usr/share/postgresql-8.3-postgis/spatial_ref_sys.sql

# RESET DB and user
echo Resetting greenline database ...
sudo -u postgres dropdb greenline
sudo -u postgres dropuser greenline

echo Creating db user
sudo -u postgres createuser --no-superuser --inherit --createrole --createdb greenline || exit 1
echo Creating db
sudo -u postgres createdb -U greenline --template template_postgis greenline || exit 1
sudo -u postgres createdb -U greenline || exit 1
sudo -u postgres createlang plpgsql greenline || exit 1
sudo -u postgres psql -d greenline -f $POSTGIS_SQL || exit 1
sudo -u postgres psql -d greenline -f $SPATIAL_REF_SQL || exit 1

export SUDO="sudo -H -E -u greenline"

echo Syncing DB...
yes no | $SUDO $VIRTUAL_ENV/bin/python ./manage.py syncdb --database=greenline || exit 1

