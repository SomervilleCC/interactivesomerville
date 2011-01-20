import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import permalink
from django.utils import simplejson
from django.utils.encoding import smart_unicode
from django_extensions.db.fields import AutoSlugField
from greenline.utils.markdowner import MarkupField

from taggit.managers import TaggableManager
from sharing.models import SharedItem
from greenline.utils.location_utils import geocode_to_point_object

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

class GeocodingException(Exception):
    pass
        
class DoesNotExist(GeocodingException):
    pass

class UnparseableLocation(GeocodingException):
    pass

class AmbiguousResult(GeocodingException):
    def __init__(self, choices, message=None):
        self.choices = choices
        if message is None:
            message = "Returned %s results" % len(choices)
        self.message = message

    def __str__(self):
        return self.message
        
class Idea(models.Model):
    """
    An Idea.
    """
    STATUS_CHOICES = (
        (0, 'Yes'),
        (1, 'No'),
    )
    
    author          = models.ForeignKey(User, blank=True, null=True) # individual user, usually the creator
    
    title           = models.CharField(
                        max_length = 100, 
                        help_text = 'A short name for this idea.')
    
    slug            = AutoSlugField(populate_from='title', max_length=64)

    address         = models.CharField(max_length=200, help_text="i.e. 83 Highland Avenue", null=True, blank=True)    
    copy            = MarkupField(blank=True, null=True, help_text='Use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown-syntax</a>' )
    geometry        = models.PointField(srid=4326, null=True, blank=True)
    tease           = models.TextField('tease', blank=True, editable=False)
    creator_ip      = models.IPAddressField(blank=True, null=True, default='127.0.0.1')
    created         = models.DateTimeField(default=datetime.datetime.now)
    share           = models.IntegerField('shared', choices=STATUS_CHOICES, default=1)
    publish         = models.DateTimeField(default=datetime.datetime.now)
    
    tags            = TaggableManager()

    class Meta:
        verbose_name        = 'idea'
        verbose_name_plural = 'ideas'
        ordering = ('-created', 'author')
        get_latest_by = 'created'

    def __unicode__(self):
        return self.title

    def get_tags(self):
        return list(self.tags.all())

    def delete(self):
        self.tags = None
        super(Idea, self).delete()
        
    @property
    def latitude(self):
        '''Get the location's latitude.'''
        return self.geometry.y

    @property
    def longitude(self):
        '''Get the location's longitude.'''
        return self.geometry.x

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ('idea_post', None, {
            'username': self.author.username,
            'year': self.publish.year,
            'month': "%02d" % self.publish.month,
            'slug': self.slug
    })
    get_absolute_url = models.permalink(get_absolute_url)

    def save(self, force_insert=False, force_update=False):
        result = None
        if not self.address:
            pass
            
        location = "%s, %s, %s" % (self.address, 'Somerville', 'MA')

        if not self.geometry:
            try:
                result = geocode_to_point_object(location)
            except AmbiguousResult:
                pass
                
        if not result:
            pass
        else:
            self.geometry = result[1]
            
        super(Idea, self).save(force_insert, force_update)

    shared = generic.GenericRelation(SharedItem)
    tags = TaggableManager()
        
# handle notification of new comments
from threadedcomments.models import ThreadedComment
def new_comment(sender, instance, **kwargs):
    if isinstance(instance.content_object, Idea):
        idea = instance.content_object
        if notification:
            notification.send([idea.author], "idea_post_comment",
                {"user": instance.user, "idea": idea, "comment": instance})
models.signals.post_save.connect(new_comment, sender=ThreadedComment)
