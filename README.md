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
 * gdal (more on this later)

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

We will install the latest stable release of Pinax (at this writing, 0.7.3). First download the tarball _Pinax-0.7.3-bundle.tar.gz_ [here](http://pinaxproject.com/downloads/). Then go to Pinax's install documentation [here](http://pinaxproject.com/docs/0.7/install/).

You might want to install PIL first. For more information on installing PIL, see [Installing PIL](http://pinaxproject.com/docs/0.7/pil/#ref-pil).

If you've got PIL working, good for you. Now we're going to make a slight adjustment to Pinax's default installation. Go to the directory where you've downloaded the tarball:

    $ tar xvfz Pinax-0.7.3-bundle.tar.gz    
    $ cd Pinax-0.7.3-bundle/requirements/base
    $ wget http://media.djangoproject.com/releases/1.1.1/Django-1.1.1.tar.gz

If you don't have _wget_, figure out another way to get Django-1.1.1.tar.gz into that directory.

Next, delete the other Django tarball (This step is not absolutely necessary, but it won't hurt.):

    $ rm Pinax-0.7.3-bundle/requirements/base/Django-1.0.4.tar.gz

And edit the libs.txt file, changing line #17 from Django==1.0.4 to Django==1.1.1:

    $ vi Pinax-0.7.3-bundle/requirements/libs.txt
    $ <change required django version>  

Now you're ready for the actual Pinax install. Pinax uses [virtualenv](http://pypi.python.org/pypi/virtualenv), it will install this for you:

    $ cd <path-to>/Pinax-0.7.3-bundle   
    $ python scripts/pinax-boot.py <path-to-virtual-env-to-create>

For example, if you want the virtualenv location to be in your home directory, you would say:

    $ python scripts/pinax-boot.py ~/pinax-env
    
Pinax recommends [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/) along with virtualenv. If you choose to use it, then the above becomes:

    $ python scripts/pinax-boot.py $WORKON_HOME/pinax-env   

Executing the pinax-boot command prints out a bunch of stuff. To get to work you now run:

    $ workon pinax-env 
    
Alternatively if you're not using [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/) you type:

    $ source <path-to-virtual-env-created>/bin/activate 
    
To test that Django and Pinax are behaving well together, you should create a quick test app in Pinax:

    (pinax-env)$ pinax-admin clone_project social_project mytest  
    
And see if it runs:

    (pinax-env)$ cd mytest/ 
    (pinax-env)$ python manage.py syncdb    
    (pinax-env)$ python manage.py runserver 