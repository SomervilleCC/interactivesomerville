from django.template import RequestContext
from django.shortcuts import render_to_response

from participation.models import Station, Line

import gpolyencode

def home(request):
	stations = Station.objects.all()
	lines = Line.objects.all()
	
	# encode linestrings
	encoder = gpolyencode.GPolyEncoder()
	for line in lines:
		line.encoded = encoder.encode(line.geometry.coords)
	
	return render_to_response("homepage.html", {
			'stations': stations,
			'lines': lines,
		}, context_instance=RequestContext(request))
