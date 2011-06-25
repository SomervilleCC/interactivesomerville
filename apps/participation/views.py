from django.template import RequestContext
from django.shortcuts import render_to_response

from participation.models import Station

def home(request):
	stations = Station.objects.all()
	
	return render_to_response("homepage.html", {
		'stations': stations
	}, context_instance=RequestContext(request))
