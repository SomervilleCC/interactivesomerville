from django import template
from django.template.defaultfilters import stringfilter

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
register.inclusion_tag("participation/_activity.html")(get_activity)