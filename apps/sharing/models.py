import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import permalink
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import simplejson
from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User
from docutils.core import publish_parts

from taggit.managers import TaggableManager
from sharing.managers import SharedItemManager

from greenline.utils.parsers import slugify
from greenline.utils import generics

from stations.models import Station

        
class SharedItem(models.Model):
    """An shared object, keyed by the user that shares it."""
    user        = models.ForeignKey(User, related_name='shares', default = 1) # default sharer is always SCC.
    share_date  = models.DateTimeField(verbose_name='date shared', default=datetime.datetime.now)
    #station     = models.ForeignKey(Station, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, 
                        verbose_name=('content type'),
                        related_name="content_type_set_for_%(class)s")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_id")
    
    class Meta:
        ordering = ('-share_date', 'user')
        get_latest_by = 'share_date'
        
    def __unicode__(self):
        return "%s: %s" % (self.content_type.model_class().__name__, self.user)
        
    def get_owner(self):
        return str(self.user.username) 
        
    def get_station(self):
        return str(self.station.name) 
        
    objects = SharedItemManager()
    tags = TaggableManager()
    
    def get_tags(self):
        return self.tags.all()
 
    @models.permalink
    def get_absolute_url(self):
        return (u'share_detail', (smart_unicode(self.id),))