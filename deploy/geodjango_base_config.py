# This is a work in progress.

def install_geodjango():
    install_geos()
    install_proj4()
    install_postgis()
    install_gdal()

def install_geos():
    """Install GEOS 3.2.1"""
    with cd('/usr/local/src'):
        run('wget -q http://download.osgeo.org/geos/geos-3.2.1.tar.bz2')
        run('tar xjf geos-3.2.1.tar.bz2 && rm geos-3.2.1.tar.bz2')
        with cd('geos-3.2.1'):
            run('./configure')
            run('make')
            sudo('make install')

def install_proj4():
    """Install Proj 4.7"""
    sudo('aptitude install -q -y unzip')
    with cd('/usr/local/src'):
        run('wget -q http://download.osgeo.org/proj/proj-4.7.0.tar.gz')
        run('wget -q http://download.osgeo.org/proj/proj-datumgrid-1.5.zip')
        run('tar xzf proj-4.7.0.tar.gz && rm proj-4.7.0.tar.gz')
        with cd('proj-4.7.0/nad'):
            run('unzip ../../proj-datumgrid-1.5.zip && rm ../../proj-datumgrid-1.5.zip')
        with cd('proj-4.7.0'):
            run('./configure')
            run('make')
            sudo('make install')

def install_postgis():
    """Install PostGIS 1.5.1"""
    sudo('aptitude install -q -y libxml2-dev postgresql-server-dev-8.3')
    with cd('/usr/local/src'):
        run('wget -q http://postgis.refractions.net/download/postgis-1.5.1.tar.gz')
        run('tar xzf postgis-1.5.1.tar.gz && rm postgis-1.5.1.tar.gz')
        with cd('postgis-1.5.1'):
            run('./configure')
            run('make')
            sudo('make install')
    sudo('ldconfig')
    sudo("""su postgres << EOF  
createdb -E UTF8 template_postgis
createlang -d template_postgis plpgsql
psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
psql -d template_postgis -f `pg_config --sharedir`/contrib/postgis-1.5/postgis.sql
psql -d template_postgis -f `pg_config --sharedir`/contrib/postgis-1.5/spatial_ref_sys.sql
psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
EOF""")
    

def install_gdal():
    """Install GDAL 1.7.1"""
    with cd('/usr/local/src'):
        run('wget -q http://download.osgeo.org/gdal/gdal-1.7.1.tar.gz')
        run('tar xzf gdal-1.7.1.tar.gz && rm gdal-1.7.1.tar.gz')
        with cd('gdal-1.7.1'):
            run('./configure')
            run('make')