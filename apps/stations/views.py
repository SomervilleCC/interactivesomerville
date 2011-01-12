import logging
import datetime
from django import http
from django.conf import settings
from django.contrib.gis.geos import *
from django.core import serializers
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, get_list_or_404, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import escape
from django.template.loader import render_to_string
from urllib2 import HTTPError
from httplib import BadStatusLine

from django.contrib.auth.decorators import login_required

from greenline.utils.location_utils import lazy_key, geocode_to_point_object, transform, boundingBox
from geopy import distance
from stations.models import Station
from django.http import HttpResponse, HttpResponseRedirect

from location.models import Location, LocationType
from stations.forms import StationForm
from photos.models import Photo

import settings

log = logging.getLogger('views')
console = logging.StreamHandler()
log.addHandler(console)

class StationBadRequest(http.HttpResponseBadRequest):
    """
    Response returned when a share post is invalid.
    """
    def __init__(self, why):
        super(StationBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("400-debug.html", {"why": why})
    
def nearest_station(location):
    ''' Return the nearest Station object 
        from a given Location object. '''
    nearest = []
    stations = Station.objects.all()
    for station in stations:
        station.radius.geometry.transform(4326)
        if station.radius.geometry.contains(location.geometry):
            nearest.append(station.name)
    return nearest
    
def nearest_station_from_geo(geometry):
    ''' Return the nearest Station object 
        from a given Point object. '''
    nearest = []
    stations = Station.objects.all()
    for station in stations:
        station.radius.geometry.transform(4326)
        if station.radius.geometry.contains(geometry):
            nearest.append(station.name)
    return nearest

def nearer_station(location, stations):
    ''' Return the nearest Station object[s] 
        from a given Location object. '''
    distance1 = distance.distance((location.y, location.x), (stations[0].latitude, stations[0].longitude))
    distance2 = distance.distance((location.y, location.x), (stations[1].latitude, stations[1].longitude))
    if (distance1 < distance2):
        return stations[0]
    return stations[1]
    
def stations(request, template_name="stations/stations.html"):
    ''' Return a random Station object, Locations, centered on the Station. '''

    random_station = Station.objects.order_by('?')[:1]
    locations = Location.objects.all()
    
    transform(random_station)
    bbox = boundingBox(random_station[0].geometry.y, random_station[0].geometry.x, .57) # .57 places it exactly on radius edge
    
    markerpos = (bbox[0], bbox[1])
                
    return render_to_response(template_name, {
    'stations': transform(Station.objects.all()),
    'random_station': random_station,
    'markerpos': markerpos,
    'stationname': random_station[0].name,
    'locations' : locations,
    'photos':   Photo.objects.all()[:10], # random photos.

    }, context_instance=RequestContext(request)
    )


def your_station(request, form_class=StationForm, template_name="stations/your_station.html"):
    ''' Request an address and return a new Location, 
        with directions to nearest Station. '''
        
    context = {'GOOGLE_API_KEY': lazy_key()}
    station = None
    geom = None
    title = None
    
    if request.method == "POST":
        result = None
        data = request.POST.copy()
        address = data.get("address")
        
        location = "%s, %s, %s" % (address, 'Somerville', 'MA')
        
        try:
            result = geocode_to_point_object(location) # result = (str, (Point object))
        except (HTTPError, BadStatusLine):
            raise StationBadRequest(request)
            
        if result:
            title = result[0]
            geom = Point(result[1][0], result[1][1])
            latitude = result[1][1]
            longitude = result[1][0]
            nearest = nearest_station_from_geo(geom)
            
            if not nearest:
                station = None
            else:
                if len(nearest) > 1:
                    station1 = nearest[0]
                    stations = list(Station.objects.filter(name=station1))
                    station2 = nearest[1]
                    stations.append(Station.objects.filter(name=station2))
                    stations = (stations[0], stations[1][0])
                    stations[0].geometry.transform(4326)
                    stations[1].geometry.transform(4326)
                    
                    station = nearer_station(geom, stations)
                else:
                    nearest = nearest[0]
                    station = Station.objects.filter(name=nearest) # a GeoQuerySet
                    station = station[0] # a Station
                    station.geometry.transform(4326)

            if station:
                exact_distance = distance.distance((latitude, longitude), (station.latitude, station.longitude)) # geopy.distance.VincentyDistance
                #log.debug('Location is  %s meters from %s', exact_distance.meters, station.name) 
                exact_distance_in_feet = exact_distance.ft
                exact_distance_in_meters = str(exact_distance.meters)
                exact_distance_in_meters = exact_distance_in_meters[:exact_distance_in_meters.rfind('.')]
                exact_distance_in_feet = str(exact_distance.feet)
                exact_distance_in_feet = exact_distance_in_feet[:exact_distance_in_feet.rfind('.')]
            else:
                raise Exception("Got an error for %s ." % escape(result[0]))
        else:
            raise Exception("Unknown geocoding error. Please try another address.")
    else:
        if request.method == 'GET':
            station_form = StationForm()        
            return render_to_response(template_name, {
                "form": station_form
            }, context_instance=RequestContext(request))
            
    return render_to_response("stations/checkin.html", {
        'name': address,
        'station': station,
        'geom': geom,
        'title': title,
        #'distance_in_meters':exact_distance_in_meters,
        'distance_in_feet':exact_distance_in_feet,
    }, context_instance=RequestContext(request))