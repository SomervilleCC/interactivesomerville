import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.contrib.auth.decorators import login_required
from django.views.generic import date_based
from django.conf import settings

from django import forms
import settings

from greenline.utils.location_utils import geocode

from ideas.forms import IdeaForm
from ideas.models import Idea

kwargs = {
    # set common filter params here
    }


def idea(request, username, year, month, slug, template_name="ideas/idea.html"):
    ''' return a single idea by user'''
    idea = Idea.objects.filter(slug=slug, publish__year=int(year), publish__month=int(month)).filter(author__username=username)
    if not idea[0].publish <= datetime.datetime.now():
        raise Http404

    if idea[0].author != request.user:
        raise Http404

    return render_to_response(template_name, {
        "idea": idea[0],
    }, context_instance=RequestContext(request))

def ideas(request, username=None, template_name="ideas/ideas.html"):
    ideas = Idea.objects.select_related(depth=1).order_by("-publish")
    if username is not None:
        user = get_object_or_404(User, username=username.lower())
        ideas = ideas.filter(author=user)
    return render_to_response(template_name, {
        "ideas": ideas,
    }, context_instance=RequestContext(request))
            
@login_required
def your_ideas(request, template_name="ideas/your_ideas.html"):
    return render_to_response(template_name, {
        "ideas": Idea.objects.filter(author=request.user),
    }, context_instance=RequestContext(request))

@login_required
def destroy(request, id):
    idea = Idea.objects.get(pk=id)
    user = request.user
    title = idea.title
    if idea.author != request.user:
            request.user.message_set.create(message="You can't delete posts that aren't yours")
            return HttpResponseRedirect(reverse("idea_list_yours"))

    if request.method == "POST" and request.POST["action"] == "delete":
        idea.delete()
        request.user.message_set.create(message=_("Successfully deleted post '%s'") % title)
        return HttpResponseRedirect(reverse("idea_list_yours"))
    else:
        return HttpResponseRedirect(reverse("idea_list_yours"))

    return render_to_response(context_instance=RequestContext(request))

@login_required
def new(request, form_class=IdeaForm, template_name="ideas/new.html"):
    if request.method == "POST":
        if request.POST["action"] == "create":
            idea_form = form_class(request.user, request.POST)
            if idea_form.is_valid():
                idea = idea_form.save(commit=False)
                idea.author = request.user
                if getattr(settings, 'BEHIND_PROXY', False):
                    idea.creator_ip = request.META["HTTP_X_FORWARDED_FOR"]
                else:
                    idea.creator_ip = request.META['REMOTE_ADDR']
                idea.save()
                # @@@ should message be different if published?
                request.user.message_set.create(message="Successfully saved post '%s'" % idea.title)

                return HttpResponseRedirect(reverse("idea_list_yours"))
        else:
            idea_form = form_class()
    else:
        idea_form = form_class()

    return render_to_response(template_name, {
        "idea_form": idea_form
    }, context_instance=RequestContext(request))

@login_required
def edit(request, id, form_class=IdeaForm, template_name="ideas/edit.html"):
    idea = get_object_or_404(Idea, id=id)

    if request.method == "POST":
        if idea.author != request.user:
            request.user.message_set.create(message="You can't edit posts that aren't yours")
            return HttpResponseRedirect(reverse("idea_list_yours"))
        if request.POST["action"] == "update":
            idea_form = form_class(request.user, request.POST, instance=idea)
            if idea_form.is_valid():
                idea = idea_form.save(commit=False)
                idea.save()
                request.user.message_set.create(message="Successfully updated post '%s'" % idea.title)

                return HttpResponseRedirect(reverse("idea_list_yours"))
        else:
            idea_form = form_class(instance=idea)
    else:
        idea_form = form_class(instance=idea)

    return render_to_response(template_name, {
        "idea_form": idea_form,
        "idea": idea,
    }, context_instance=RequestContext(request))

# Users
def user_list(request):
    """
    docstring cometh
    """
    queryset = User.objects.extra(
        select={
            'idea_count': 'SELECT COUNT(*) FROM ideas_idea WHERE author_id = auth_user.id',
        }
    )
    return object_list(request, queryset,
        paginate_by=ITEMS_PER_PAGE, allow_empty=True,
        template_object_name='user', template_name='ideas/user_list.html')

def user_detail(request, user_id):
    """
    docstring cometh
    """
    queryset = User.objects.extra(
        select={
            'idea_count': 'SELECT COUNT(*) FROM ideas_idea WHERE author_id = auth_user.id',
        }
    )
    return object_detail(request, queryset, object_id=user_id,
        template_object_name='user_info', template_name='ideas/user_detail.html')
