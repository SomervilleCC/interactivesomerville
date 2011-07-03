from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import fromstr
from django.utils import simplejson

from participation.models import Station, Line, Theme, Shareditem, Idea, Meetingnote, Newsarticle, Media
from participation.forms import IdeaForm

import gpolyencode
import oembed


def get_greenline():
	""" Query Greenline and return encoded polylines optimized for Google Maps. """
	
	greenline = Line.objects.all()
	
	# encode linestrings
	encoder = gpolyencode.GPolyEncoder()
	for line in greenline:
		line.encoded = encoder.encode(line.geometry.coords)
		
	return greenline
	

def home(request):
	""" Homepage, including Activity Stream. """
	
	stations = Station.objects.all()
	activities = Shareditem.objects.all()[:10].select_subclasses()
	lines = get_greenline()
	
	return render_to_response("homepage.html", locals(), context_instance=RequestContext(request))

	
def station_areas_list(request):
	
	stations = Station.objects.all().order_by('id')
	# TODO: paginate
	activities = Shareditem.objects.filter(station__isnull=False).select_subclasses()
	lines = get_greenline()
	
	return render_to_response("participation/station_areas_list.html", locals(), context_instance=RequestContext(request))

		
def station_area_detail(request, slug):

	station = get_object_or_404(Station.objects, slug=slug)
	# TODO: paginate
	activities = Shareditem.objects.filter(station=station).select_subclasses()
	lines = get_greenline()
	
	return render_to_response("participation/station_area_detail.html", locals(), context_instance=RequestContext(request))


def get_nearest_station(request):
	""" Find the nearest station for a lat/lon coordinate pair. """
		
	try:
		location = fromstr("POINT(%s %s)" % (request.GET['lng'], request.GET['lat']), srid=4326)
		# find nearest station
		station = Station.objects.distance(location).order_by("distance")[0]
		# json response
		response = dict(name=station.name, url=station.get_absolute_url(), lat=station.geometry.y, lng=station.geometry.x)
		return HttpResponse( simplejson.dumps(response), content_type = "application/javascript; charset=utf8" )
	except:
		return redirect("home")

	
def themes_list(request):

	themes = Theme.objects.all().order_by('id')
	activities = Shareditem.objects.filter(theme__isnull=False).select_subclasses()
	lines = get_greenline()

	return render_to_response("participation/themes_list.html", locals(), context_instance=RequestContext(request))

		
def theme_detail(request, slug):

	theme = get_object_or_404(Theme.objects, slug=slug)
	# TODO: paginate
	activities = Shareditem.objects.filter(theme=theme).select_subclasses()
	lines = get_greenline()

	return render_to_response("participation/theme_detail.html", locals(), context_instance=RequestContext(request))


def idea_detail(request, id):

	idea = get_object_or_404(Idea.objects.select_related(), pk=id)
	
	return render_to_response("participation/idea_detail.html", {
			"idea": idea,
			"lines": get_greenline() if idea.station else None # render lines only in combination with station
		}, 
		context_instance=RequestContext(request))


@login_required
def share(request):
	""" Sharing form for all options (models). """
	
	ideaform = IdeaForm()
	
	return render_to_response("participation/form.html", {
		"ideaform": ideaform,
		"stations": Station.objects.all().order_by('id'),
		"lines": get_greenline(),
		}, 
		context_instance=RequestContext(request))


@login_required
def add_idea(request):
	""" Add a new Idea. """
	
	if request.method == "POST":
		idea = Idea()
		ideaform = IdeaForm(request.POST, instance=idea)
		idea.ip = request.META['REMOTE_ADDR']
		idea.author = request.user
		
		if ideaform.is_valid():
			ideaform.save()
			return redirect("idea_detail", id=idea.id)
		else:
			return render_to_response("participation/form.html", {
				"ideaform": ideaform,
				"stations": Station.objects.all().order_by('id'),
				"lines": get_greenline(),
			},
			context_instance=RequestContext(request))
	else:
		return redirect("share") # empty share form

def meetingnote_detail(request, id):

	meetingnote = get_object_or_404(Meetingnote.objects.select_related(), pk=id)
	lines = get_greenline() if meetingnote.station else None

	return render_to_response("participation/meetingnote_detail.html", locals(), context_instance=RequestContext(request))


def newsarticle_detail(request, id):

	newsarticle = get_object_or_404(Newsarticle.objects.select_related(), pk=id)
	lines = get_greenline() if newsarticle.station else None

	return render_to_response("participation/newsarticle_detail.html", locals(), context_instance=RequestContext(request))


def media_detail(request, id):
	
	media = get_object_or_404(Media.objects.select_related(), pk=id)
	
	oembed.autodiscover()
	resource = oembed.site.embed(media.url)
	
	if resource.provider_name == u"Flickr":
		embed_code = "<a href='%s'><img src='%s' width='%s' height='%s' alt='%s' ></a>" % (media.url, resource.url, resource.width, resource.height, resource.title)
	else:
		embed_code = resource.html
	
	lines = get_greenline() if media.station else None

	return render_to_response("participation/media_detail.html", locals(), context_instance=RequestContext(request))


