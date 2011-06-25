from django.contrib.gis.db import models
from django.db.models import permalink

from greenline.utils.markdowner import MarkupField

# workaround for South custom fields issues 
try:
	from south.modelsinspector import add_introspection_rules
	add_introspection_rules([], ['^django\.contrib\.gis\.db\.models\.fields\.PointField'])
	add_introspection_rules([], ['^django\.contrib\.gis\.db\.models\.fields\.LineStringField'])
	add_introspection_rules([], ['^greenline\.utils\.markdowner\.MarkupField'])
except ImportError:
	pass

class Station(models.Model):
	""" A Greenline station """
	
	name = models.CharField(max_length=36)
	slug = models.SlugField(max_length=36)
	desc = MarkupField("Description", blank=True, null=True, help_text="Use <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown-syntax</a>")
	
	geometry = models.PointField(geography=True) # default SRS 4326
	objects = models.GeoManager()
	
	def __unicode__(self):
		return u"%s"% (self.name)

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
		return u'%s' % self.title
