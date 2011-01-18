import os

from django.views.generic.simple import direct_to_template
from account.openid_consumer import PinaxConsumer
from django.conf.urls.defaults import *
from django.contrib.auth.views import *
from django.conf import settings

from greenline.utils.location_utils import transform, nearest_stations

from photos.models      import Photo
from location.models    import Location
from stations.models    import Station
from ideas.models       import Idea
from sharing.models     import SharedItem
from principles.models  import Entry


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', direct_to_template, {
        "template": "homepage.html",
            'extra_context': {
            "shares":       SharedItem.objects.all().order_by("-share_date")[:15],
            'ideas':        Idea.objects.order_by('?')[:3], # random ideas.
            'stations':     transform(Station.objects.all()),
            'photos':       Photo.objects.order_by('?')[:20], # random photos.
            'locations':    Location.objects.all(), # random places.
            'random_station' :  transform(Station.objects.order_by('?')[:1]) # center on random station.
        },
    }, name="home"),
    
    # pinax provided
    (r'^account/',  include('account.urls')),
    (r'^announcements/', include('announcements.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^about/',    include('about.urls')),
    (r'^notices/',  include('notification.urls')), # needed for threadedcomments
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^admin/(.*)', admin.site.root),

    # greenline provided
    (r'^ideas/',    include('ideas.urls')),
    (r'^principles/', include('principles.urls')),
    (r'^sharing/',  include('sharing.urls')),
    (r'^location/', include('location.urls')),
    (r'^stations/', include('stations.urls')),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/', include('staticfiles.urls')),
    )