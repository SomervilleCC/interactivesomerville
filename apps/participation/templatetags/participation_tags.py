from django import template
from django.template.defaultfilters import stringfilter
from django.db.models import Count

from participation.models import Shareditem

register = template.Library()


@register.filter
@stringfilter
def fixbackslash(value):
	"""Replace backslashes '\'  in encoded polylines for Google Maps overlay."""
	return value.replace('\\','\\\\')


def get_activity(activity):
	""" Returns resource for given external media object """
	if activity.itemtype == "e" and activity.url:
		resource = activity.get_oembed()
		return {
			'activity': activity,
			'resource': resource,
		}

	return {
		'activity': activity,
	}

ITEMTYPES_DISPLAY = {
	'i': 'Ideas',
	'm': 'Meeting Notes',
	'n': 'Newspaper Article',
	'e': 'Photos & Videos',
	'd': "Data",
}

def get_station_stats(station):
	""" Returns aggregated counts for Shareditems per station """

	stats = Shareditem.objects.filter(station=station).values('itemtype').order_by().annotate(Count('itemtype'))
	# [{'itemtype__count': 4, 'itemtype': u'e'}]
	
	for stat in stats:
		stat['itemtype_display'] = ITEMTYPES_DISPLAY[stat['itemtype']]
	
	return {
		'station': station,
		'stats': stats,
	}

register.inclusion_tag("participation/_activity.html")(get_activity)
register.inclusion_tag("participation/_station_stats.html")(get_station_stats)