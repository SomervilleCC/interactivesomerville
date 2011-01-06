from django.views.generic.simple import direct_to_template
from django.conf.urls.defaults import *
from django.contrib.auth.views import *
from django.contrib import admin
from django.conf import settings
import sharing.views as share_views
import os

from django.conf.urls.defaults import *
from sharing.models import SharedItem
from sharing.forms import SharedForm, SharedFormGET
from voting.views import vote_on_object

urlpatterns = patterns('',

    url(r'^$', view=share_views.shares_latest, name="shares_index"),
    url(r'^latest/$', view=share_views.shares_latest, name="shares_index"),
    url(r'^new/$', view=share_views.new, name="share_new"),
    url(r'^submit/$', direct_to_template, {"template": "sharing/submit.html"}, name="submit"),
    
    
    url(r'^(?P<share_id>\d+)/$', share_views.share_detail,  name='share_detail'),
    
    # for voting
    (r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$',
        vote_on_object, dict(
            model=SharedItem,
            template_object_name='share',
            template_name='sharing/share_confirm_vote.html',
            allow_xmlhttprequest=True)),
            
    (r'^validate/$', 'ajax_validation.views.validate', {'form_class': SharedFormGET, 'callback': lambda request, *args, **kwargs: {'user': request.user}}, 'share_form_validate'),

)