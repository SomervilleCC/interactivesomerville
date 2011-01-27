from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from geopy import geocoders, distance, util

import settings

from location.models import Location
from location.forms import LocationForm
from stations.models import Station, Route, Radius
from greenline.utils.location_utils import transform, boundingBox


def locations(request, template_name="location/locations.html"):
    locations = Location.objects.order_by('?')[:30]
                    
    return render_to_response(template_name, {
    'stations': transform(Station.objects.all()),
    'locations' : locations
    }, context_instance=RequestContext(request)
    )
    
@login_required
def your_locations(request, template_name="location/your_locations.html"):
    return render_to_response(template_name, {
        "locations": Location.objects.filter(author=request.user),
    }, context_instance=RequestContext(request))
    
    
@login_required
def new(request, form_class=LocationForm, template_name="location/new.html"):
    if request.method == "POST":
        if request.POST["action"] == "create":
            location_form = form_class(request.user, request.POST)
            if location_form.is_valid():
                location = location_form.save(commit=False)
                location.author = request.user
                location.save()

                request.user.message_set.create(message="Successfully saved location '%s'" % location.title)

                return HttpResponseRedirect(reverse("location_list_yours"))
        else:
            location_form = LocationForm()
    else:
        if request.method == 'GET':
            location_form = LocationForm()

    return render_to_response(template_name, {
        "form": location_form
    }, context_instance=RequestContext(request))

@login_required
def destroy(request, id):
    location = Location.objects.get(pk=id)
    user = request.user
    title = idea.title
    if location.author != request.user:
            request.user.message_set.create(message="You can't delete locations that aren't yours")
            return HttpResponseRedirect(reverse("location_list_yours"))

    if request.method == "POST" and request.POST["action"] == "delete":
        location.delete()
        request.user.message_set.create(message=_("Successfully deleted location '%s'") % title)
        return HttpResponseRedirect(reverse("location_list_yours"))
    else:
        return HttpResponseRedirect(reverse("location_list_yours"))

    return render_to_response(context_instance=RequestContext(request))


def near_stations(location):
    ''' finds the closet station from an arbitrary point'''
    distances = []
    stations = transform(Station.objects.all())
    for station in stations:
        distances.append(distance.distance((location.geometry.y, location.geometry.x), (station.latitude, station.longitude)))
    return distances    

def nearer_station(location, stations):
    ''' Takes a location (Point) object and a tuple of two Station objects'''
    distance1 = distance.distance((location.y, location.x), (stations[0].latitude, stations[0].longitude))
    distance2 = distance.distance((location.y, location.x), (stations[1].latitude, stations[1].longitude))
    if (distance1 < distance2):
        return stations[0]
    return stations[1]