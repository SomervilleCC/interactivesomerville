import textwrap
import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape
from django.utils import datastructures, simplejson

from django.contrib.comments.views.utils import next_redirect
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.contrib.comments import signals, get_form, get_model

from mptt_comments.decorators import login_required_ajax

def _lookup_content_object(data):
    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    parent_pk = data.get("parent_pk")
    
    if parent_pk:
        try:
            parent_comment = get_model().objects.get(pk=parent_pk)
            target = parent_comment.content_object
            model = target.__class__
        except get_model().DoesNotExist:
            return CommentPostBadRequest(
                "Parent comment with PK %r does not exist." % \
                    escape(parent_pk))
    elif ctype and object_pk:
        try:
            parent_comment = None
            model = models.get_model(*ctype.split(".", 1))
            target = model._default_manager.get(pk=object_pk)
        except TypeError:
            return CommentPostBadRequest(
                "Invalid content_type value: %r" % escape(ctype))
        except AttributeError:
            return CommentPostBadRequest(
                "The given content-type %r does not resolve to a valid model." % \
                    escape(ctype))
        except ObjectDoesNotExist:
            return CommentPostBadRequest(
                "No object matching content-type %r and object PK %r exists." % \
                    (escape(ctype), escape(object_pk)))
    else:
        return CommentPostBadRequest("Missing content_type or object_pk field.")

    return (target, parent_comment, model)

def new_comment(request, parent_pk=None, content_type=None, object_pk=None, *args, **kwargs):
    """
    Display the form used to post a reply. 
    
    Expects a comment_id, and an optionnal 'is_ajax' parameter in request.GET.
    """
    
    is_ajax = request.GET.get('is_ajax') and '_ajax' or ''
    data = {
        'parent_pk': parent_pk,    
        'content_type': content_type,
        'object_pk': object_pk,
    }
    response = _lookup_content_object(data)
    if isinstance(response, HttpResponse):
        return response
    else:
        target, parent_comment, model = response
    
    # Construct the initial comment form
    form = get_form()(target, parent_comment=parent_comment)
        
    template_list = [
        "comments/%s_%s_new_form%s.html" % tuple(str(model._meta).split(".") + [is_ajax]),
        "comments/%s_new_form%s.html" % (model._meta.app_label, is_ajax),
        "comments/new_form%s.html" % is_ajax,
    ]
    return render_to_response(
        template_list, {
            "form" : form,
        }, 
        RequestContext(request, {})
    )

@login_required_ajax
@login_required
def post_comment(request, next=None, *args, **kwargs):
    """
    Post a comment.

    HTTP POST is required unless a initial form is requested. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``comments/preview.html``, will be rendered.
    """

    # Require POST
    if request.method != 'POST':
        return HttpResponseNotAllowed(["POST"])
    
    is_ajax = request.POST.get('is_ajax') and '_ajax' or ''

    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()

    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name()
        if not data.get('email', ''):
            data["email"] = request.user.email

    response = _lookup_content_object(data)
    if isinstance(response, HttpResponse):
        return response
    else:
        target, parent_comment, model = response

    # Do we want to preview the comment?
    preview = data.get("submit", "").lower() == "preview" or \
              data.get("preview", None) is not None
        
    # Construct the comment form 
    form = get_form()(target, parent_comment=parent_comment, data=data)
            
    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the comment
    if form.errors or preview:
        template_list = [
            "comments/%s_%s_preview%s.html" % tuple(str(model._meta).split(".") + [is_ajax]),
            "comments/%s_preview%s.html" % (model._meta.app_label, is_ajax),
            "comments/preview%s.html" % is_ajax
        ]
        data = {
            'comment': form.data.get("comment", ""),
            'parent': parent_comment,
            'level': parent_comment and parent_comment.level or 0,
            'title': form.data.get("title", ""),
            'submit_date': datetime.datetime.now(),
            'rght': 0,
            'lft': 0,
            'user': request.user,
            'user_name' : request.user.username,
        }
        comment = get_model()(**data)
        return render_to_response(
            template_list, {
                "comment" : comment,
                "form" : form,
                "allow_post": not form.errors,
                "is_ajax" : is_ajax,
            }, 
            RequestContext(request, {})
        )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    comment.user = request.user
    comment.user_name = request.user.username

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )
    
    return next_redirect(data, next, 'comments-comment-done%s' % (is_ajax and '-ajax' or ''), c=comment._get_pk_val())
    
def confirmation_view(template, doc="Display a confirmation view.", is_ajax=False, *args, **kwargs):
    """
    Confirmation view generator for the "comment was
    posted/flagged/deleted/approved" views.
    
    The HTTP Status code will be different depending on the comment used:
    - 201 Created for a is_public=True comment
    - 202 Accepted for a is_public=False comment
    """
    def confirmed(request):
        comment = None
        if 'c' in request.GET:
            try:
                comment = get_model().objects.get(pk=request.GET['c'])
            except ObjectDoesNotExist:
                pass

        response = HttpResponse(
            render_to_string(
                template, {
                    'comment': comment,
                    'is_ajax': is_ajax,
                    'success' : True
                },
                RequestContext(request)
            )
        )
        response.status_code = comment.is_public and 201 or 202
        return response

    confirmed.__doc__ = textwrap.dedent("""\
        %s

        Templates: `%s``
        Context:
            comment
                The posted comment
        """ % (doc, template)
    )
    return confirmed
    
comment_done_ajax = confirmation_view(
    template = "comments/posted_ajax.html",
    doc = """Display a "comment was posted" success page.""",
    is_ajax = True,
)

comment_done = confirmation_view(
    template = "comments/posted.html",
    doc = """Display a "comment was posted" success page."""
)


    
def comment_tree_json(request, object_list, tree_id, cutoff_level, bottom_level):
    
    if object_list:
        json_comments = {'end_level': object_list[-1].level, 'end_pk': object_list[-1].pk}
          
        template_list = [
            "comments/display_comments_tree.html",
        ]
        json_comments['html'] = render_to_string(
            template_list, {
                "comments" : object_list,
                "cutoff_level": cutoff_level,
                "bottom_level": bottom_level,
                "is_ajax" : True,
            }, 
            RequestContext(request, {})
        )
        
        return json_comments
    return {}

def comments_more(request, from_comment_pk, restrict_to_tree=False, *args, **kwargs):

    comment = get_model().objects.select_related('content_type').get(pk=from_comment_pk)

    offset = getattr(settings, 'MPTT_COMMENTS_OFFSET', 20)
    collapse_above = getattr(settings, 'MPTT_COMMENTS_COLLAPSE_ABOVE', 2)
    cutoff_level = getattr(settings, 'MPTT_COMMENTS_CUTOFF', 3)
    bottom_level = 0
             
    qs = get_model().objects.filter_hidden_comments().filter(
        content_type=comment.content_type,
        object_pk=comment.object_pk,
        level__lte=cutoff_level
    )
    
    part1 = Q(tree_id=comment.tree_id) & Q(lft__gte=comment.lft + 1)
    if restrict_to_tree:
        # Here we only want the nodes with the same root-id and a greater lft value. 
        qs = qs.filter(part1)
        bottom_level = comment.level + 1
    else:
        # Here we need all nodes with a different root-id, or all nodes with
        # the same root-id and a greater lft value. 
        # The default order should do the right thing
        # 
        # FIXME: it expects tree_id to be in chronological order!
        part2 = Q(tree_id__gt=comment.tree_id)
        qs = qs.filter(part1 | part2)
        
    until_toplevel = []
    remaining = []
    toplevel_reached = False
    remaining_count = qs.count() - offset
    
    for comment in qs[:offset]:
        
        if comment.level == 0:
            toplevel_reached = True
            
        if toplevel_reached:
            remaining.append(comment)
        else:
            until_toplevel.append(comment)
    
    json_data = {'remaining_count': remaining_count, 'comments_for_update': [], 'comments_tree': {} }
    if restrict_to_tree:
        json_data['tid'] = comment.get_root().id
    else:
        json_data['tid'] = 0
    
    for comment in until_toplevel:    
        json_comment = {'level': comment.level, 'pk': comment.pk, 'parent' : comment.parent_id}
        template_list = [
            "comments/display_comment.html",
        ]
        json_comment['html'] = render_to_string(
            template_list, {
                "comment" : comment,
                "cutoff_level": cutoff_level,
                "collapse_levels_above": collapse_above,
                "is_ajax" : True,
            }, 
            RequestContext(request, {})
        )
        json_data['comments_for_update'].append(json_comment)
        
    json_data['comments_tree'] = comment_tree_json(request, remaining, comment.tree_id, cutoff_level, bottom_level)
    
    return HttpResponse(simplejson.dumps(json_data), mimetype='application/json')
    
def comments_subtree(request, from_comment_pk, include_self=None, include_ancestors=None, *args, **kwargs):
    
    comment = get_model().objects.select_related('content_type').get(pk=from_comment_pk)     
    
    cutoff_level = comment.level + getattr(settings, 'MPTT_COMMENTS_CUTOFF', 3)
    bottom_level = not include_ancestors and (comment.level - (include_self and 1 or 0)) or 0
    
    qs = get_model().objects.filter_hidden_comments().filter(
        tree_id=comment.tree_id, 
        lft__gte=comment.lft + (not include_self and 1 or 0),
        lft__lte=comment.rght,
        level__lte=cutoff_level - (include_self and 1 or 0)
    )
    
    is_ajax = request.GET.get('is_ajax') and '_ajax' or ''
    
    if is_ajax:    
        
        json_data = {'comments_for_update': [], 'comments_tree': {} }
        json_data['comments_tree'] = comment_tree_json(request, list(qs), comment.tree_id, cutoff_level, bottom_level)
        
        return HttpResponse(simplejson.dumps(json_data), mimetype='application/json')
        
    else:
        
        target = comment.content_object
        model = target.__class__

        template_list = [
            "comments/%s_%s_subtree.html" % tuple(str(model._meta).split(".")),
            "comments/%s_subtree.html" % model._meta.app_label,
            "comments/subtree.html"
        ]
        
        comments = list(qs)
        if include_ancestors:
            comments = list(comment.get_ancestors()) + comments
        
        return render_to_response(
            template_list, {
                "object" : target,
                "detail_comment" : comment,
                "comments" : comments,
                "bottom_level": bottom_level,
                "cutoff_level": cutoff_level - 1,
                "collapse_levels_above": getattr(settings, 'MPTT_COMMENTS_COLLAPSE_ABOVE', 2),
                "collapse_levels_below": getattr(settings, 'MPTT_COMMENTS_COLLAPSE_BELOW_DETAIL', True) and comment.level or 0
            }, 
            RequestContext(request, {})
        )

def count_for_object(request, content_type_id, object_pk, mimetype='text/plain'):
    """
    Returns the comment count for any object defined by content_type_id and object_id or slug.
    Mimetype defaults to plain text.
    """
    try:
        ctype = ContentType.objects.get_for_id(content_type_id)
    except ObjectDoesNotExist:
        raise Http404("No content found for id %s" % content_type_id)
    count = str(get_model().objects.filter(object_pk=object_pk, content_type=ctype).count())
    return HttpResponse(count, mimetype = mimetype)
