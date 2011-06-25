from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from pinax.apps.account.openid_consumer import PinaxConsumer


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
#    url(r"^$", direct_to_template, {
#        "template": "homepage.html",
#    }, name="home"),
	url(r"^$", "participation.views.home", name="home"),

	url(r"^station-areas/$", "participation.views.station_areas_list", name="station_areas_list"),
	url(r"^station-areas/(?P<slug>[-\w]+)/$", "participation.views.station_area_detail", name="station_area_detail"),
	
	url(r"^themes/$", "participation.views.themes_list", name="themes_list"),
	url(r"^themes/(?P<slug>[-\w]+)/$", "participation.views.theme_detail", name="theme_detail"),

    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^openid/", include(PinaxConsumer().urls)),
    url(r"^profiles/", include("idios.urls")),
    url(r"^notices/", include("notification.urls")),
    url(r"^announcements/", include("announcements.urls")),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
