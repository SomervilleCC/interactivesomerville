# Interactive Somerville #

_Interactive Somerville_ is a tool for visualizing issues, asking questions, learning facts, and contributing ideas related to the Greenline Extension Project in Somerville, MA.

## Fresh Start ##

This is a fresh start, intentended to migrate the existing code base for Pinax 0.7 in the [legacy branch](https://github.com/SomervilleCC/interactivesomerville/tree/legacy) to [Pinax 0.9 fresh-start](https://github.com/pinax/pinax/tree/fresh-start).

A Pinax basic project served as starting point.

### Installation and getting started ###

#### Create a virtual environment (recommended)

Follow the documentation at [virtualenv](http://www.virtualenv.org/) or [virtualenvwrapper](http://pypi.python.org/pypi/virtualenvwrapper). If you're using virtualenvwrapper, then create a new virtual environment with

    $ mkvirtualenv interactivesomerville --no-site-packages

#### Checkout the project

    $ git clone git://github.com/SomervilleCC/interactivesomerville.git

#### Install all project requirements (Django, Pinax, etc.):

    $ cd interactivesomerville
    $ pip install -r requirements/project.txt

#### Install PostgreSQL/PostGIS and geographic libaries

    $ sudo apt-get install binutils python-setuptools postgresql-8.4-postgis postgresql-server-dev-8.4 python-psycopg2 gdal-bin python-gdal libproj-dev

#### Create PostGIS template

...on Ubuntu 10.10 with PostGIS 1.5 for instance:

    $ sudo su postgres
    $ POSTGIS_SQL_PATH=/usr/share/postgresql/8.4/contrib/postgis-1.5
    $ createdb -E UTF8 template_postgis
    $ createlang -d template_postgis plpgsql
    $ psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
    $ psql -d postgres -c "update pg_database set datistemplate = false where datname = 'template_postgis';"
    $ psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql
    $ psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
    $ psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
    $ psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
    $ psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"

Please see [GeoDjango installation docs](https://docs.djangoproject.com/en/1.3/ref/contrib/gis/install/) for more detailed information and troubleshooting.

#### Create interactivesomerville database user

    $ createuser interactivesomerville
    $ #Shall the new role be a superuser? (y/n) n
    $ #Shall the new role be allowed to create databases? (y/n) y
    $ #Shall the new role be allowed to create more new roles? (y/n) n
    $ psql
    $ ALTER ROLE interactivesomerville WITH password 'password';
    $ \q
    $ exit

#### Create new user interactivesomerville

    $ sudo adduser interactivesomerville

#### Create interactivesomerville database

    $ sudo su - interactivesomerville
    $ createdb interactivesomerville -T template_postgis

#### Add your database configuration

    DATABASES = {
	    "default": {
	        "ENGINE": "django.contrib.gis.db.backends.postgis",
	        "NAME": "interactivesomerville",
	        "USER": "interactivesomerville",
	        "PASSWORD": "password",
	        "HOST": "",
	        "PORT": "",
	    }
	}

.. to `settings.py` or create a `local_settings.py` (recommended)

#### Syncronize database and run the development server

    $ python manage.py syncdb
    $ python manage.py runserver


#### Test the application

...in your localhost at [http://127.0.0.1:8000](http://127.0.0.1:8000)

