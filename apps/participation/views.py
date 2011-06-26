from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from participation.models import Station, Line, Theme, Idea

import gpolyencode

def home(request):
	stations = Station.objects.all()
	
	return render_to_response("homepage.html", {
			"stations": stations,
			"lines": lines(),
		}, 
		context_instance=RequestContext(request))

def lines():
	""" Query Greenline and return encoded polylines optimized for Google Maps. """
	lines = Line.objects.all()
	
	# encode linestrings
	encoder = gpolyencode.GPolyEncoder()
	for line in lines:
		line.encoded = encoder.encode(line.geometry.coords)
		
	return lines
	
def station_areas_list(request):
	stations = Station.objects.all().order_by('id')
	
	return render_to_response("participation/station_areas_list.html", {
			"stations": stations,
		}, 
		context_instance=RequestContext(request))
		
def station_area_detail(request, slug):
	station = get_object_or_404(Station.objects, slug=slug)
	
	return render_to_response("participation/station_area_detail.html", {
			"station": station,
			"lines": lines(),
		},
		context_instance=RequestContext(request))
	
def themes_list(request):
	themes = Theme.objects.all().order_by('id')

	return render_to_response("participation/themes_list.html", {
			"themes": themes,
		}, 
		context_instance=RequestContext(request))
		
def theme_detail(request, slug):
	theme = get_object_or_404(Theme.objects, slug=slug)

	return render_to_response("participation/theme_detail.html", {
			"theme": theme,
		},
		context_instance=RequestContext(request))
		
def idea_detail(request, id):
	idea = get_object_or_404(Idea.objects.select_related(), pk=id)
	
	return render_to_response("participation/idea_detail.html", {
			"idea": idea,
			"lines": lines() if idea.station else None # render lines only in combination with station
		}, 
		context_instance=RequestContext(request))
