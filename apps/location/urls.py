from django.conf.urls.defaults import *

from django.conf.urls.defaults import patterns, url
from threadedcomments.models import FreeThreadedComment
from threadedcomments import views

from django.views.generic import list_detail
from voting.views import vote_on_object

from location.models import Location
from location.forms import LocationForm

import location.views

free = {'model' : FreeThreadedComment}
vote_on_idea_dict = {}

urlpatterns = patterns('',

    url(r'^$', view=location.views.locations, name='locations'),
    url(r'^new/$', view=location.views.new, name='location_new'),
    url(r'^your_locations/$', view=location.views.your_locations, name='location_list_yours'),    
    (r'^validate/$', 'ajax_validation.views.validate', {'form_class': LocationForm, 'callback': lambda request, *args, **kwargs: {'user': request.user}}, 'location_form_validate'),
    )
