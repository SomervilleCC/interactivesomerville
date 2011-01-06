import datetime
from django.db import models
from django.db.models import permalink
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django_extensions.db.fields import AutoSlugField
from django.contrib.contenttypes import generic
from taggit.managers import TaggableManager

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None
    
class Route(models.Model):

    segment = models.CharField(max_length=36, )
    geometry = models.LineStringField(srid=26986) #EPSG:26986 Mass State Plane
    objects = models.GeoManager()
    
    objects = models.GeoManager()
    tags    = TaggableManager()

    def __unicode__(self):
        return u"%s"% (self.segment)
            
    def get_absolute_url(self):
        pass

    class Meta:
        db_table = u'route'

class Radius(models.Model):
    
    name            = models.CharField(max_length=36, )
    geometry        = models.PolygonField(srid=26986) #EPSG:26986 Mass State Plane
    
    def __unicode__(self):
        return u"%s"% (self.name)

    objects = models.GeoManager()
    tags    = TaggableManager()

    def get_absolute_url(self):
        pass

    class Meta:
        db_table = u'radius'

class Station(models.Model):
    ''' A Greenline station '''

    name = models.CharField(max_length=36, )
    slug = AutoSlugField(populate_from='name')
    copy = models.TextField(blank=True, null=True)    

    geometry    = models.PointField(srid=26986) #EPSG:26986 Mass State Plane
    route       = models.ForeignKey(Route, blank=True, null=True)
    radius      = models.ForeignKey(Radius, blank=True, null=True)
    users       = models.ManyToManyField(User, blank=True, related_name='user_station')
    
    objects = models.GeoManager()

    tags        = TaggableManager()

    def __unicode__(self):
        return u"%s"% (self.name)

    @property
    def latitude(self):
        '''Get the location's latitude.'''
        return self.geometry.y
        
    @property
    def longitude(self):
        '''Get the location's longitude.'''
        return self.geometry.x
                
    @property
    def circleVarName(self):
        '''google map hook'''
        mark = []
        mark.append(self.slug.replace('-', '').rstrip('station'))
        mark.append('Circle')
        return ''.join(mark)
        
    @property
    def markerVarName(self):
        mark = []
        mark.append(self.slug.replace('-', '').rstrip('station'))
        mark.append('Marker')
        return ''.join(mark)
    
    @permalink
    def get_absolute_url(self):
        return ('station_detail', None, { 'slug': self.slug } )

    class Meta:
        db_table = u'station'
