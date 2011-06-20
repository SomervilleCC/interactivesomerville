from django.contrib.auth.decorators import permission_required

from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext

from principles.models import Principle, Entry

from stations.models import Station
from location.models import Location, LocationType
from greenline.utils.location_utils import *

import settings

def index(request):
    """
    Output a full description of each principle.
    """
    principles = Principle.objects.all()
    context = {'principles': principles}
    return render_to_response('principles/index.html', context,
        RequestContext(request))

def detail(request, principle_slug):
	"""
	Output principle detail page with all related content.
	"""
	
	principle = get_object_or_404(Principle.objects, slug=principle_slug)
	
	entries = Entry.objects.filter(principle=principle)
	
	return render_to_response('principles/detail.html',{
		'principle': principle,
		'entries': entries,
	}, RequestContext(request))

def entry(request, principle_slug, entry_slug):
	"""
	Output a full individual entry; this is the view for an entry's permalink.
	"""
	
	principle = get_object_or_404(Principle.objects, slug=principle_slug)
	
	entry = get_object_or_404(Entry.objects, principle=principle, slug=entry_slug)

	context = {
		'entry': entry,
	}
	return render_to_response('principles/entry.html', context, RequestContext(request))


def entry_index(request):
    """
    Output...
    """
    stations = transform(Station.objects.all())
    entries = Entry.objects.all()
    latest_entry = Entry.objects.latest()
    principles = Principle.objects.all()
    recent_entries = Entry.objects.published().exclude(id=latest_entry.id)[:5]
#    years_with_entries = Entry.objects.published().dates('published', 'year')
#    months_with_entries = Entry.objects.published().dates('published', 'month')
#    days_with_entries = Entry.objects.published().dates('published', 'day')
    context = {
        'principles': principles,
        'latest_entry': latest_entry,
        'recent_entries': recent_entries,
        'entries': entries,        
        'stations': stations
    }
    return render_to_response('principles/entry_index.html', context,
        RequestContext(request))
        
def entry_archive_year(request, year):
    """Output the published entries for a given year."""
    entries = get_list_or_404(Entry.objects.published(), published__year=year)
    years_with_entries = Entry.objects.published().dates('published', 'year')
    entries_by_month = dict.fromkeys(range(1, 13), 0)
    for entry in entries:
        entries_by_month[entry.published.month] += 1
    context = {
        'year': year,
        'entries': entries,
        'entries_by_month': entries_by_month,
        'max_entries_per_month': max(entries_by_month.values()),
        'years_with_entries': years_with_entries,
    }
    return render_to_response('principles/entry_archive_year.html', context,
        RequestContext(request))



def entry_detail_year(request, year, slug):
    """
    Output a full individual entry; this is the view for an entry's permalink.
    """
    entry = get_object_or_404(Entry.objects.published(), published__year=year,slug=slug)
    context = {'entry': entry}
    return render_to_response('principles/entry_detail.html', context,
        RequestContext(request))


@permission_required('principles.change_entry', '/admin/')
def entry_preview(request, year, slug):
    """
    Allows draft entries to be viewed as if they were publicly available
    on the site.  Draft entries with a ``published`` date in the
    future are visible too.  The same template as the ``entry_detail``
    view is used.
    """
    entry = get_object_or_404(Entry.objects.filter(status=Entry.DRAFT_STATUS),
        published__year=year, slug=slug)
    context = {'entry': entry}
    return render_to_response('blog/entry_detail.html', context,
        RequestContext(request))