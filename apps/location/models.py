import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.conf import settings
from django.db.models import permalink
from django_extensions.db.fields import AutoSlugField
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError

from taggit.managers import TaggableManager

from sharing.managers import SharedItemManager
from sharing.models import SharedItem
from stations.models import Station, Radius, Route
from principles.models import Principle
from greenline.utils.location_utils import geocode_to_point_object
from greenline.utils.markdowner import MarkupField
from greenline.utils.parsers import slugify

import logging

log = logging.getLogger("greenline.sharing.models")
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.DEBUG)

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


class LocationType(models.Model):
    ''' Type of place '''

    title       = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(
                    max_length=64,
                    help_text="Automatically generated from title. Must be unique.")

    objects     = models.GeoManager()

    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        verbose_name = 'location type'
        verbose_name_plural = 'location types'
        db_table = 'location_types'
        
    @permalink
    def get_absolute_url(self):
        return ('location_type_detail', None, {'title': self.title})


class Location(models.Model):
    ''' Location of interest '''
    
    author          = models.ForeignKey(User, blank=True, null=True) # individual user, usually the creator
    
    title           = models.CharField(
                        max_length = 100, 
                        help_text = 'A short name for this location.')
    
    slug            = AutoSlugField(populate_from='title', max_length=64)

    address         = models.CharField(max_length=200, help_text="i.e. 83 Highland Avenue")    
    description     = MarkupField(blank=True, null=True, help_text='Use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown-syntax</a>' )
    geometry        = models.PointField(srid=4326, null=True, blank=True)
    location_type   = models.ForeignKey(LocationType, blank=True, null=True, help_text="i.e. school, park, playground.")
    station         = models.ForeignKey(Station, blank=True, null=True)
    created         = models.DateTimeField(default=datetime.datetime.now)
    principle       = models.ForeignKey(Principle, blank=True, null=True, help_text="Associate with a principle?")
        
    objects         = models.GeoManager()
    tags            = TaggableManager()
        
    shared = generic.GenericRelation(SharedItem)

    def __unicode__(self):
        return '%s' % (self.title)

    @property
    def latitude(self):
        '''Get the location's latitude.'''
        return self.geometry.y
        
    @property
    def longitude(self):
        '''Get the location's longitude.'''
        return self.geometry.x
    
    @property
    def get_static_url(self):
        return "http://maps.google.com/maps/api/staticmap?zoom=14&size=250x100&maptype=terrain&markers=color:green|label:L|%s,%s&style=feature:road.highway|element:geometry|hue:0xff0022|saturation:60|lightness:-20&style=feature:road.arterial|element:geometry|hue:0x2200ff|lightness:-40:visibility:simplified|saturation:30&style=feature:road.local|hue:0xf6ff00|saturation:60|gamma:0.7|visibility:simplified&style=feature:water|element:geometry|saturation:40|lightness:40&style=road.highway|element:labels|visibility:on|saturation:98&style=feature:administrative.locality|element:labels|hue:0x0022ff|saturation:50|lightness:-10|gamma:0.9&style=feature:transit.line|element:geometry|hue:0xff0000|visibility:on|lightness:-70&sensor=false" % (self.geometry.y, self.geometry.x)

    @property
    def circleVarName(self):
        '''google map javascript hack'''
        mark = []
        mark.append(self.slug.replace('-', ''))
        mark.append('Circle')
        return ''.join(mark)
        
    @property
    def markerVarName(self):
        mark = ['_'] # leading underscore avoids javascript variable name error
        mark.append(self.slug.replace('-', ''))
        mark.append('Marker')
        return ''.join(mark)

    def get_tags(self):
        return list(self.tags.all())

    def delete(self):
        self.tags = None
        super(Location, self).delete()
        
    @permalink
    def get_absolute_url(self):
        return ('location_detail', None, { 'slug': self.slug } )
        
    class Meta:
        get_latest_by = 'created'
        
    def save(self, force_insert=False, force_update=False):
        if not self.address:
            raise ValidationError(u'Location object must be initialized with an address.')
            
        location = "%s, %s, %s" % (self.address, 'Somerville', 'MA')

        if not self.geometry:
            try:
                result = geocode_to_point_object(location)
            except AmbiguousResult:
                pass
                
        if result:
            self.title = result[0]
            self.geometry = result[1]
        else:
            raise Exception(u'Failed to geocode address.')
                
        super(Location, self).save()
        
    def save_as_shared(self):
        result = super(Location, self).save()
        if result is None:
            # default to SCC admin user
            if self.author == None:
                return SharedItem.objects.create_or_update(
                    instance = self, 
                    timestamp = datetime.datetime.now(),
                )
            else:
                return SharedItem.objects.create_or_update(
                    user = self.author,
                    instance = self, 
                    timestamp = datetime.datetime.now(),
                )