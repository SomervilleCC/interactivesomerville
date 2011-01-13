import sys
from django.conf import settings
from django.contrib.gis.geos import *
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.gdal import CoordTransform, SpatialReference 
from django.core import serializers
import re
from httplib import BadStatusLine
#from stations.models import Station, Radius

from django.utils.safestring import mark_safe
from django.utils import simplejson

from geopy import geocoders, distance, util
import types

import math

GOOGLE_API_KEY = None

def lazy_key():
    global GOOGLE_API_KEY
    if GOOGLE_API_KEY is not None:
        return GOOGLE_API_KEY
    try:
        GOOGLE_API_KEY = getattr(settings, 'GOOGLE_API_KEY')
        return GOOGLE_API_KEY
    except AttributeError:
        raise ImproperlyConfigured('requires a valid key')

def transform(stations):
    ct = CoordTransform(SpatialReference(26986), SpatialReference(4326))
    stats = []
    for station in stations:
        station.geometry.transform(ct)
        stats.append(station)
    return stats
    
def geocode(address):
    result = None
    g = geocoders.Google(resource='maps', format_string="%s, Somerville MA")
    try:
        result = g.geocode(address)
    except (ValueError, UnboundLocalError):
        return None
    return result
    
def geocode_to_point_object(address):
    somerville = '(S|s)omerville(,| )'
    medford = '(M|m)edford(,| )'

    if re.search(medford, address):
        g = geocoders.Google(resource='maps', format_string="%s, Medford MA")
    elif re.search(somerville, address):
        g = geocoders.Google(resource='maps', format_string="%s, Somerville MA")
    else:
        g = geocoders.Google(resource='maps', format_string="%s, MA")
    
    try:
        result = g.geocode(address)
    except (ValueError, UnboundLocalError):
        return None
        
    title = result[0]
    # reversed for spatial databases x, y must be lng/lat while for Google API x, y it is lat/lng
    lnglat = (result[1][1], result[1][0])
    result = (title, Point(lnglat))
    return result
    
def reverse_geocode(point):
    ''' Point argument must be tuple: (latitude, longitude)''' 
    geoc = geocoders.Google(lazy_key())
    result = geoc.reverse(point, exactly_one=True) # FIXME: handle multiple results
    place = result[0]
    return place  # geopy.util.RichResult

# degrees to radians
def deg2rad(degrees):
    return math.pi*degrees/180.0
# radians to degrees
def rad2deg(radians):
    return 180.0*radians/math.pi

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]

# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )

# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)

    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius

    return (rad2deg(latMin), rad2deg(lonMin), rad2deg(latMax), rad2deg(lonMax))