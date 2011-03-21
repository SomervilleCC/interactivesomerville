##GREENLINE
_Greenline_ (aka inTeractiveSomerville) is a tool for visualizing issues, asking questions, learning facts, and contributing ideas related to the Greenline Extension Project in Somerville, MA.

###GETTING STARTED

This document is designed to help you get up and running with the code. There's a bit of work involved and not every step is fully documented (working on that). Nevertheless, if you're interested in geospatial development, Django, Pinax and the other technologies, it's a worthwhile endeavor.

This project is released under a [Creative Commons Attribution 3.0 Unported License](http://creativecommons.org/licenses/by/3.0/). We invite you to clone, hack, and otherwise enjoy yourself!

###System Requirements

OSX, Linux, or other Unix flavor...

####You need:

 * python **2.6** (2.7 might work; 2.5 may not)
 * Django **1.1.1**
 * Pinax **0.7.3**
 * Postgresql **8.3**, **8.4**
 * PostGIS **1.4** or **1.5**
 * libgdal

####Optional but helpful:
 * pip
 * virtualenv
 * git
 * wget
 * unzip

##Background
####New to Python?
An excellent tutorial is [here](http://docs.python.org/tutorial/), a good read is [Dive Into Python](http://diveintopython.org/). For folks on the go try [Instant Python](http://hetland.org/writing/instant-python.html).

####New to Django?
To learn Django you should start by reading the documentation, then try the [tutorial](http://docs.djangoproject.com/en/dev/intro/tutorial01).   Substantial changes to Django have been made in the recent past, here we're focused on [version 1.1.1](http://docs.djangoproject.com/en/1.1/). 

####What's Pinax?
Web sites have many common elements: registration, a blog, wiki, photos, tagging and so on. Designing and developing all this from scratch each time is a dreadful bore. As a balm Pinax has collected a bunch of Django apps that you can use, so you don't need to start from scratch every time. Pinax helps you re-use software that others in the community have already built and tested for you. Now wasn't that nice of them?
 
##Installation - Django and Pinax

Django is a _web framework_. Pinax is a _meta-web-framework_ built on top of Django. You can safely forget the word _meta_ and all of this will work just fine.

We install the latest stable release of Pinax (at this writing, 0.7.3). Download the tarball _Pinax-0.7.3-bundle.tar.gz_ [here](http://pinaxproject.com/downloads/). Then go to Pinax's install documentation [here](http://pinaxproject.com/docs/0.7/install/).

We'll make a slight adjustment to Pinax's default installation. Pinax 0.7.3 runs Django 1.0.4 by default but we're going to run Django 1.1.1. Go into the directory where you've downloaded the tarball and unpack:

    $ tar xvfz Pinax-0.7.3-bundle.tar.gz    
    $ cd Pinax-0.7.3-bundle/requirements

Using a text editor, edit the libs.txt file:

    $ vi libs.txt
    $ (change line 18 from Django==1.0.4 to Django==1.1.1)
    $ (change line 21 from geopy==0.93dev-r0 to geopy==0.94)

Next, edit the Pinax script pinax-boot.py, lines 1134 to 1143, so that they now read:

    $   PINAX_MUST_HAVES = {
    $       'setuptools-git': ('0.3.4', 'setuptools_git-0.3.4.tar.gz'),
    $       'setuptools-dummy': ('0.0.3', 'setuptools_dummy-0.0.3.tar.gz'),
    $       'Django': ('1.1.1', 'Django-1.1.1.tar.gz'),
    $   }

    $   DJANGO_VERSIONS = (
    $       # '1.0.4',
    $       '1.1.1',
    $   )

Save and cd back up to the Pinax install directory:

    $ cd <path-to>/Pinax-0.7.3-bundle   

Now issue the following command:

    $ ./scripts/pinax-boot.py --no-site-packages --distribute ~/greenline

The last argument to pinax-boot.py (~/greenline) is the location of the virtualenv root directory.
    
Pinax also recommends [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/) along with virtualenv. If you use this, then the above command becomes:

    $ ./scripts/pinax-boot.py --no-site-packages --distribute  $WORKON_HOME/greenline   

Executing pinax-boot.py in this way sets up an isolated virtualenv. Once this is done, then execute:

    $ workon greenline 
    
If you're not using [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/) alternatively you type:

    $ source <path-to-virtual-env>/bin/activate 

Check that Django and Pinax are behaving well together by creating and running a test app. At this point you should be running inside your virtualenv:

    (greenline)$ pinax-admin clone_project social_project mytest
    (greenline)$ cd mytest
    (greenline)$ ./manage.py runserver

You should see Pinax's social app running at http://localhost:8000. 
    
To run Greenline you install some additional libs located in greenline's src requirements.txt file. Clone the repository and cd into that directory:

    (greenline)$ git clone git@github.com:gerlad/greenline.git
    (greenline)$ cd greenline
    
Now execute the following:

    (greenline)$ pip install -r requirements.txt
    
    
##Installation - PostGIS

Installing Postgresql and PostGIS depends on your platform; here's some help:

####On Ubuntu 9.10 (Karmic)
    
    apt-get install python2.6 \
    python2.6-dev \
    build-essential \
    git \
    subversion \
    postgresql-8.3-postgis \
    libgdal1-1.5.0 \
    libgdal1-dev \
    libxml2 \
    libxml2-dev \
    libxslt1.1 \
    libxslt1-dev \
    libproj0 \
    libproj-dev \
    unzip \
    wget
    
####On Mac OS X

Using  [Homebrew](http://blog.apps.chicagotribune.com/2010/02/17/quick-install-pythonpostgis-geo-stack-on-snow-leopard/).

Using  [MacPorts](http://www.macports.org/).

    $ port install git-core postgresql83 postgis gdal libxml2 libxslt

There are many possible permutations of postgresl version and platform. If you're running Mac X here's a good place [to start](http://docs.djangoproject.com/en/1.2/ref/contrib/gis/install/#mac-os-x) for that OS.

There's excellent documentation provided by the Django Project on GIS support in general, specifically for running [GeoDjango](http://docs.djangoproject.com/en/1.2/ref/contrib/gis/install/).

##Installation - Creating the spatial database template

Once you have the basic postgresql and PostGIS installs complete, you'll want to setup a spatial template. The are a number of steps involved in the process of enabling spatial functionality, thus we create a template that can be reused. 

A good resource for completing this step can be found [here](http://docs.djangoproject.com/en/1.2/ref/contrib/gis/install/#creating-a-spatial-database-template-for-postgis)


