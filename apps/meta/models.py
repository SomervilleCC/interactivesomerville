from django.db import models

from utils.markdowner import MarkupField

class Page(models.Model):
	""" A theme to guide and categorize user contributions and conversations"""
	
	title = models.CharField(max_length=100)
	slug = models.SlugField(max_length=100)
	content = MarkupField(help_text="Use <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown-syntax</a>")
	order = models.IntegerField(default=1)
	
	class Meta:
		ordering = ("order",)
	
	def __unicode__(self):
		return u"%s" % self.title
		
	@models.permalink
	def get_absolute_url(self):
		return ("meta_page", None, { "slug": self.slug, })