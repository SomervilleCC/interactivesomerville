from django.contrib.gis.db import models
from django.db.models import permalink
from django.contrib.auth.models import User

from greenline.utils.markdowner import MarkupField

# workaround for South custom fields issues 
try:
	from south.modelsinspector import add_introspection_rules
	add_introspection_rules([], ['^django\.contrib\.gis\.db\.models\.fields\.PointField'])
	add_introspection_rules([], ['^django\.contrib\.gis\.db\.models\.fields\.LineStringField'])
	add_introspection_rules([], ['^greenline\.utils\.markdowner\.MarkupField'])
except ImportError:
	pass

def get_sentinel_user():
	""" Cascading rule if user is removed. """
	return User.objects.get_or_create(username='deleted')[0]


class Station(models.Model):
	""" A Greenline station """
	
	name = models.CharField(max_length=36)
	slug = models.SlugField(max_length=36)
	desc = MarkupField("Description", blank=True, null=True, help_text="Use <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown-syntax</a>")
	
	geometry = models.PointField(geography=True) # default SRS 4326
	objects = models.GeoManager()
	
	def __unicode__(self):
		return u"%s"% (self.name)
		
	@permalink
	def get_absolute_url(self):
		return ("station_area_detail", None, { "slug": self.slug, })


class Line(models.Model):
	""" The Greenline """
	
	geometry = models.LineStringField(geography=True)
	objects = models.GeoManager()

	
class Theme(models.Model):
	""" A theme to guide and categorize user contributions and conversations"""
	
	title = models.CharField(max_length=100)
	slug = models.SlugField(max_length=100)
	desc = MarkupField("Description", blank=True, null=True, help_text="Use <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown-syntax</a>")
	
	def __unicode__(self):
		return u"%s" % self.title
		
	@permalink
	def get_absolute_url(self):
		return ("theme_detail", None, { "slug": self.slug, })
		

class Idea(models.Model):
	""" A user submitted idea relating to a station area, theme. """
	
	# keep it simple: textfield only
	desc = MarkupField("Description", blank=True, null=True, help_text="Use <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown-syntax</a>")
	
	station = models.ForeignKey('Station', null=True, blank=True)
	theme = models.ForeignKey('Theme', null=True, blank=True)
	author = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
	
	ip = models.IPAddressField(default='127.0.0.1')
	created = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now_add=True, auto_now=True)
	
	geometry = models.PointField(geography=True, null=True, blank=True) # default SRS 4326
	objects = models.GeoManager()
	
	class Meta:
		ordering = ('-created', 'author')
		get_latest_by = 'created'
	
	def __unicode__(self):
		return u"%i" % self.id
		
	@permalink
	def get_absolute_url(self):
		return ("idea_detail", None, { "id": self.id, })
