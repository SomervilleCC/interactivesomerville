import datetime

from django.db import models
from django.contrib.gis.db import models
from django.db.models import permalink
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.utils.encoding import smart_unicode

from docutils.core import publish_parts
from taggit.managers import TaggableManager

from sharing.models import SharedItem
from sharing.managers import SharedItemManager

from greenline.utils.parsers import slugify
from greenline.utils import generics

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None
    
class VideoSource(models.Model):
    """
    An encapsulation for "embed template".
    """
    name = models.CharField(max_length=200)
    home = models.URLField()
    embed_template = models.URLField()
    
    def __unicode__(self):
        return self.name

class Video(models.Model):
    """ Model based on Youtube. """

    author      = models.CharField(max_length=150)
    video_id    = models.CharField(max_length=50)
    source      = models.ForeignKey(VideoSource, related_name="videos")
    title       = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    url         = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    geometry    = models.PointField(srid=4326, null=True, blank=True)
    view_count  = models.PositiveIntegerField(null=True, blank=True, editable=False)
    
    # Date metadata
    date_uploaded = models.DateTimeField(blank=True, null=True)
    date_received  = models.DateTimeField(blank=True, null=True)

    objects     = models.GeoManager()

    def __unicode__(self):
        return u'%s' % self.title
        
    def timestamp(self):
        return self.date_received
    timestamp = property(timestamp)
    
    def embed_url(self):
        return u'http://www.youtube.com/v/%s' % self.video_id
    
    shared = generic.GenericRelation(SharedItem)
        