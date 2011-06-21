import os
from django.contrib.gis.utils import LayerMapping
from participation.models import Station

station_mapping = {
	'name' : 'NAME', 
	'geometry' : 'POINT',
}

station_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/stations_4326.shp'))

def run(verbose=True):
	lm = LayerMapping(Station, station_shp, station_mapping, transform=False, encoding='iso-8859-1')
	lm.save(strict=True, verbose=verbose)