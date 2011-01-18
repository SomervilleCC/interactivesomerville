import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import permalink
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils import simplejson
from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User

from taggit.managers import TaggableManager
from django_extensions.db.fields import AutoSlugField
from greenline.utils.markdowner import MarkupField

from sharing.models import SharedItem
from greenline.utils.parsers import slugify

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from threadedcomments.models import ThreadedComment

PRINCIPLE_CHOICES = ( \
    (1, 'More Local Jobs'), \
    (2, 'Increase Commercial and Economic Development'), \
    (3, 'Keep and Add Local Businesses'), \
    (4, 'Keep Somerville Affordable'), \
    (5, 'Maintain Our Diversity'), \
    (6, 'Improve the Green Environment'), \
    (7, 'Encourage Walking and Biking'), \
    (8, 'Create Community Gathering Spaces'), \
    (9, 'Improve Access'), \
    (10, 'Community Involvement'), \
    (11, 'Connecting Buses and Trains'))
    

class Principle(models.Model):

    title = models.CharField(
        max_length=200, 
        help_text='Name of this principle.'
        )

    slug = models.SlugField(
        help_text="Automatically generated from title."
        ) 
        
    body = MarkupField(blank=True, null=True, 
        help_text='Use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown-syntax</a>' )

    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        verbose_name = 'principle'
        verbose_name_plural = 'principles'
        db_table = 'principles'
        
        
class Entry(models.Model):
    ''' Represents an entry on one of the 11 Principles.'''
            
    STATUS_CHOICES = (
        (0, 'Inactive'),
        (1, 'Active'),
    )
    
    PUBLISHED_STATUS = 1
    DAYS_COMMENTS_ENABLED = 30

    principle = models.ForeignKey(Principle, blank=True, null=True)
    
    title = models.CharField(
        max_length=200, 
        help_text='Name of this entry.'
        )
    slug = models.SlugField(
        help_text="Automatically generated from title."
        )   
    author = models.ForeignKey(
        User,
        help_text="User creating this entry.", 
        blank=True, null=True
        )

    body = MarkupField(blank=True, null=True, 
        help_text='Use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown-syntax</a>' )
    
    status          = models.IntegerField(choices=STATUS_CHOICES, default=1)
    
    latitude        = models.FloatField(null=True, blank=True, editable=False)
    longitude       = models.FloatField(null=True, blank=True, editable=False)

    created         = models.DateTimeField(verbose_name='date_created', default=datetime.datetime.now)
    published       = models.DateTimeField(verbose_name='date published', default=datetime.datetime.now)
    enable_comments = models.BooleanField(default=False)
    
    shared          = generic.GenericRelation(SharedItem)
    tags            = TaggableManager()
    
    def __unicode__(self):
        return "%s"% (self.title)

    @property    
    def is_active(self):
        """
        Return true if this entry is active
        """
        return (self.status == self.PUBLISHED_STATUS and
            self.published <= datetime.datetime.now())
            
    @property
    def markerVarName(self):
        mark = []
        mark.append(self.slug.replace('-', ''))
        mark.append('Marker')
        return ''.join(mark)
            
    @permalink
    def get_absolute_url(self):
        return ('principle_entry_detail', None, { 'slug': self.slug } )

    class Meta:
        db_table = u'principles_entry'
        get_latest_by = 'created'
        ordering = ('-created', )