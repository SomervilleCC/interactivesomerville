import datetime

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.conf.urls.defaults import patterns, url

from django.shortcuts import render_to_response, get_object_or_404, Http404
from django.views.generic.simple import direct_to_template
from django.views.generic import list_detail
from django.template import RequestContext
from django.conf import settings
from django.contrib.gis.geos import *
from django.contrib.auth.models import User

from threadedcomments.models import FreeThreadedComment
from threadedcomments import views

free = {'model' : FreeThreadedComment}
from voting.views import vote_on_object

from principles.models import Principle
from principles.forms import PrincipleForm
import principles.views as principle_views

urlpatterns = patterns('',
    url(r'^$', principle_views.index, name='principle_index'),
	url(r'^(?P<principle_slug>[-\w]+)/$',view=principle_views.detail, name="principle_detail"),
	url(r'^(?P<principle_slug>[-\w]+)/(?P<entry_slug>[-\w]+)/$',view=principle_views.entry, name="principle_entry"),
)