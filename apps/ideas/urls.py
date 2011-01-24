from django.conf.urls.defaults import *

from django.conf.urls.defaults import patterns, url
from threadedcomments.models import FreeThreadedComment
from threadedcomments import views

free = {'model' : FreeThreadedComment}
from django.views.generic import list_detail
from voting.views import vote_on_object

from ideas.models import Idea
from ideas.forms import IdeaForm
import ideas.views as idea_views


vote_on_idea_dict = {}

urlpatterns = patterns('',

    # all idea posts
    url(r'^$', 'ideas.views.ideas', name="idea_list_all"),
    url(r'^(?P<username>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[-\w]+)/$', 'ideas.views.idea', name='idea_post'),
    url(r'^new/$', 'ideas.views.new', name='idea_new'),
    url(r'^edit/(\d+)/$', 'ideas.views.edit', name='idea_edit'),
    url(r'^your_ideas/$', 'ideas.views.your_ideas', name='idea_list_yours'),
    url(r'^destroy/(\d+)/$', 'ideas.views.destroy', name='idea_destroy'),

    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/$', views.comment, name="tc_comment"),
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$', views.comment, name="tc_comment_parent"),
    url(r'^comment/(?P<object_id>\d+)/delete/$', views.comment_delete, name="tc_comment_delete"),
    url(r'^comment/(?P<edit_id>\d+)/edit/$', views.comment, name="tc_comment_edit"),
        
    # ajax validation
    (r'^validate/$', 'ajax_validation.views.validate', {'form_class': IdeaForm, 'callback': lambda request, *args, **kwargs: {'user': request.user}}, 'idea_form_validate'),

    # for voting
    (r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$',
        vote_on_object, dict(
            model=Idea,
            template_object_name='idea',
            template_name='ideas/idea_confirm_vote.html',
            allow_xmlhttprequest=True)
            ),
)