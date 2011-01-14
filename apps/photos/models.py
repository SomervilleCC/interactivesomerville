import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import permalink
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import simplejson
from django.utils.encoding import smart_unicode
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User

from docutils.core import publish_parts
from taggit.managers import TaggableManager

from sharing.models import SharedItem
from sharing.managers import SharedItemManager

from greenline.utils.parsers import slugify
from greenline.utils import generics
from greenline.utils.location_utils import reverse_geocode

CC_LICENSES = (
    ('http://creativecommons.org/licenses/by/2.0/',         'CC Attribution'),
    ('http://creativecommons.org/licenses/by-nd/2.0/',      'CC Attribution-NoDerivs'),
    ('http://creativecommons.org/licenses/by-nc-nd/2.0/',   'CC Attribution-NonCommercial-NoDerivs'),
    ('http://creativecommons.org/licenses/by-nc/2.0/',      'CC Attribution-NonCommercial'),
    ('http://creativecommons.org/licenses/by-nc-sa/2.0/',   'CC Attribution-NonCommercial-ShareAlike'),
    ('http://creativecommons.org/licenses/by-sa/2.0/',      'CC Attribution-ShareAlike'),
)

class BigIntegerField(models.IntegerField):
    """
    Defines a PostgreSQL compatible IntegerField needed to prevent 'integer out of range' with large numbers.
    """
    def get_internal_type(self):
        return 'BigIntegerField'

    def db_type(self):
        if settings.DATABASE_ENGINE == 'oracle':
            db_type = 'NUMBER(19)'
        else:
            db_type = 'bigint'
        return db_type
        
        
class Photo(models.Model):
    """
    Model based on Flickr.
    
    """
    # Key Flickr info
    photo_id    = BigIntegerField(unique=True, editable=False, null=True) # BigIntegerField is required by postgresql.
    farm_id     = models.PositiveSmallIntegerField(null=True)
    server_id   = models.PositiveSmallIntegerField(null=True)
    secret      = models.CharField(max_length=30, blank=True)

    # Rights metadata
    taken_by    = models.CharField(max_length=100, blank=True)
    cc_license  = models.URLField(blank=True, choices=CC_LICENSES)

    # Main metadata
    title           = models.CharField(max_length=250)
    description     = models.TextField(blank=True)
    comment_count   = models.PositiveIntegerField(max_length=5, default=0)

    # Date metadata
    date_uploaded = models.DateTimeField(blank=True, null=True)
    date_received  = models.DateTimeField(blank=True, null=True, default=datetime.datetime.now)
    
    # Location metadata
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    accuracy = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    
    # Place and neighborhood
    neighbourhood = models.CharField(max_length=25, null=True, blank=True, editable=False) # spelled neighbourhood, not neighborhood!
    
    tags = TaggableManager()
    
    class Meta:
        get_latest_by = 'date_received'
        
    # EXIF metadata
    _exif = models.TextField(blank=True)
    def _set_exif(self, d):
        self._exif = simplejson.dumps(d)
    def _get_exif(self):
        if self._exif:
            return simplejson.loads(self._exif)
        else:
            return {}
    exif = property(_get_exif, _set_exif, "Photo EXIF data, as a dict.")

    def _get_farm(self):
        if self.farm_id:
            return ''.join(["farm",str(self.farm_id),"."])
        return ''
    farm = property(_get_farm)

    def __unicode__(self):
        return self.title

    def url(self):
        return "http://www.flickr.com/photos/%s/%s/" % (self.taken_by, self.photo_id)
    url = property(url)

    def timestamp(self):
        return self.date_uploaded
    timestamp = property(timestamp)

    def geometry(self):
        return Point(self.latitude, self.longitude, srid=4326)
    geometry = property(geometry)

    def address(self):
        return reverse_geocode(self.latitude, self.longitude)
    address = property(address)
            
    ### Image URLs ###

    def get_image_url(self, size=None):
        if size in list('mstbo'):
            return "http://%sstatic.flickr.com/%s/%s_%s_%s.jpg" % \
                (self.farm, self.server_id, self.photo_id, self.secret, size)
        else:
            return "http://%sstatic.flickr.com/%s/%s_%s.jpg" % \
                (self.farm, self.server_id, self.photo_id, self.secret)

    image_url       = property(lambda self: self.get_image_url())
    square_url      = property(lambda self: self.get_image_url('s'))
    thumbnail_url   = property(lambda self: self.get_image_url('t'))
    small_url       = property(lambda self: self.get_image_url('m'))
    large_url       = property(lambda self: self.get_image_url('b'))
    original_url    = property(lambda self: self.get_image_url('o'))

    ### Rights ###

    def license_code(self):
        if not self.cc_license:
            return None
        path = urlparse.urlparse(self.cc_license)[2]
        return path.split("/")[2]
    license_code = property(license_code)

    def taken_by_me(self):
        return self.taken_by == getattr(settings, "FLICKR_USERNAME", "")
    taken_by_me = property(taken_by_me)
    
    shared = generic.GenericRelation(SharedItem)