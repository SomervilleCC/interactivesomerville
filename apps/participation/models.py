from django.contrib.gis.db import models
from django.db.models import permalink
from django.contrib.auth.models import User

from utils.markdowner import MarkupField
from utils.fileupload import ContentTypeRestrictedFileField
from model_utils.managers import InheritanceManager


# South introspection rules for unsupported fields
try:
	from south.modelsinspector import add_introspection_rules
	add_introspection_rules([], ['^django\.contrib\.gis\.db\.models\.fields\.PointField'])
	add_introspection_rules([], ['^django\.contrib\.gis\.db\.models\.fields\.LineStringField'])
	add_introspection_rules([], ['^utils\.markdowner\.MarkupField'])
	add_introspection_rules([], ['^utils\.fileupload\.ContentTypeRestrictedFileField'])
except ImportError:
	pass


def get_sentinel_user():
	""" Cascading rule if user is removed. """
	return User.objects.get_or_create(username='deleted')[0]


class Station(models.Model):
	""" A Greenline station """
	
	name = models.CharField(max_length=50)
	slug = models.SlugField(max_length=50)
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
		
		
class Shareditem(models.Model):
	""" Parent model for all shared items on the page. """
	
	ITEMTYPES = (
		("i", "Idea"),
		("m", "Meeting Note"),
		('n', "Newspaper Article"),
		('e', "External Media"),
		('d', "Data"),
	)
	
	desc = MarkupField("Description", help_text="Use <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown-syntax</a>")
	itemtype = models.CharField(max_length=1, choices=ITEMTYPES, )
	
	station = models.ForeignKey("Station", null=True, blank=True)
	theme = models.ForeignKey("Theme", null=True, blank=True)
	author = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
	
	ip = models.IPAddressField(default="127.0.0.1")
	created = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now_add=True, auto_now=True)
	
	objects = InheritanceManager()
	
	class Meta:
		ordering = ("-created", "author")
		get_latest_by = "created"
	
	def __unicode__(self):
		return u"%i" % self.id
	
	
class Idea(Shareditem):
	""" A user submitted idea relating to a station area, theme. """
	
	geometry = models.PointField(geography=True, null=True, blank=True) # default SRS 4326
	objects = models.GeoManager()
	
	def save(self, *args, **kwargs):
		self.itemtype = "i"
		super(Idea, self).save(*args, **kwargs)
		
	@permalink
	def get_absolute_url(self):
		return ("idea_detail", None, { "id": self.id, })
			
		
class Meetingnote(Shareditem):
	""" A Meeting Notes/Minutes document provided via file upload or as linked resource. """
	
	meeting_date = models.DateField(blank=True, null=True,)
	note_file = ContentTypeRestrictedFileField(
		help_text="Please upload only .pdf or .doc, max. 2.5MB.", 
		upload_to="meetingnotes", 
		content_types=["application/pdf", "application/msword", "text/plain", "application/vnd.oasis.opendocument.text", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"], 
		max_upload_size=2621440,
		blank=True, null=True, 
	)
	note_url = models.URLField("URL to external notes", null=True, blank=True)
	
	geometry = models.PointField(geography=True, null=True, blank=True) # default SRS 4326
	objects = models.GeoManager()
	
	def save(self, *args, **kwargs):
		self.itemtype = "m"
		super(Meetingnote, self).save(*args, **kwargs)
		
	@permalink
	def get_absolute_url(self):
		return ("meetingnote_detail", None, { "id": self.id, })
		
		
class Newsarticle(Shareditem):
	""" A Newspaper article as linked resource. """

	url = models.URLField("Article URL", null=True, blank=True)

	geometry = models.PointField(geography=True, null=True, blank=True) # default SRS 4326
	objects = models.GeoManager()

	def save(self, *args, **kwargs):
		self.itemtype = "n"
		super(Newsarticle, self).save(*args, **kwargs)

	@permalink
	def get_absolute_url(self):
		return ("newsarticle_detail", None, { "id": self.id, })
		
		
class Media(Shareditem):
	""" An external media item (photo, video, etc.) linked with oEmbed. """

	url = models.URLField(null=True, blank=True)

	geometry = models.PointField(geography=True, null=True, blank=True) # default SRS 4326
	objects = models.GeoManager()

	class Meta:
		verbose_name_plural = "Media"

	def save(self, *args, **kwargs):
		self.itemtype = "e"
		super(Media, self).save(*args, **kwargs)

	@permalink
	def get_absolute_url(self):
		return ("media_detail", None, { "id": self.id, })

		
class Data(Shareditem):
	""" A data entry provided via file upload or as linked resource. """

	data_file = ContentTypeRestrictedFileField(
		help_text="Allowed file types are: .xls, .csv., .zip, .json; max. 10MB.", 
		upload_to="data", 
		content_types=["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.oasis.opendocument.spreadsheet", "text/csv", "application/json", "application/zip"], 
		max_upload_size=10485760,
		blank=True, null=True, 
	)
	data_url = models.URLField("URL to external data source", null=True, blank=True)

	geometry = models.PointField(geography=True, null=True, blank=True) # default SRS 4326
	objects = models.GeoManager()

	def save(self, *args, **kwargs):
		self.itemtype = "d"
		super(Data, self).save(*args, **kwargs)
