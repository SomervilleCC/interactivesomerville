from django import template

from meta.models import Page

register = template.Library()

def render_meta_links():
	""" 
	Returns a list with links to all available meta pages.
	Used as footer for instance.
	"""
	
	pages = Page.objects.all()
	
	return {
		'pages': pages,
	}

register.inclusion_tag("meta/_meta_links.html")(render_meta_links)