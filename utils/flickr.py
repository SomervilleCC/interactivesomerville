import datetime
import logging
import urllib
from django.utils import simplejson
from django.conf import settings
from django.db import transaction
from django.utils.encoding import smart_unicode

from photos.models import Photo
from sharing.models import SharedItem
from sharing.managers import SharedItemManager

from greenline.utils import parsers

log = logging.getLogger('greenline')
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.INFO)

log = logging.getLogger("greenline.flickr")


# FlickrClient API

class FlickrError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message
    def __str__(self):
        return 'FlickrError %s: %s' % (self.code, self.message)

class FlickrClient(object):
    def __init__(self, api_key, method='flickr'):
        self.api_key = api_key
        self.method = method
        
    def __getattr__(self, method):
        return FlickrClient(self.api_key, '%s.%s' % (self.method, method))
        
    def __repr__(self):
        return "<FlickrClient: %s>" % self.method
        
    def __call__(self, **params):
        params['method'] = self.method
        params['api_key'] = self.api_key
        params['format'] = 'json'
        params['nojsoncallback'] = '1'
        url = "http://flickr.com/services/rest/?" + urllib.urlencode(params)
        json = parsers.getjson(url)
        if json.get("stat", "") == "fail":
            raise FlickrError(json["code"], json["message"])
        return json

# Public API
#
def enabled():
    ok = (hasattr(settings, "FLICKR_API_KEY") and
          hasattr(settings, "FLICKR_USER_ID") and
          hasattr(settings, "FLICKR_USERNAME"))
    if not ok:
      log.warn('The Flickr provider is not available because the '
               'FLICKR_API_KEY, FLICKR_USER_ID, and/or FLICKR_USERNAME settings '
               'are undefined.')
    return ok
    
def update():
    flickr = FlickrClient(settings.FLICKR_API_KEY)
    
    # Preload the list of licenses
    licenses = licenses = flickr.photos.licenses.getInfo()
    licenses = dict((l["id"], smart_unicode(l["url"])) for l in licenses["licenses"]["license"])
    
    # Handle update by pages until we see photos we've already handled
    # FIXME!
    last_update_date = datetime.datetime(1969, 12, 31, 19, 0) 
    page = 1
    while True:
        log.debug("Fetching page %s of photos", page)
        resp = flickr.groups.pools.getPhotos(group_id=settings.FLICKR_GROUP_ID, extras="license,date_taken", per_page="500", page=str(page))
        photos = resp["photos"]
        if page > photos["pages"]:
            log.debug("Ran out of photos; stopping.")
            break
            
        for photodict in photos["photo"]:
            timestamp = parsers.parsedate(str(photodict["datetaken"]))
            if timestamp < last_update_date:
                log.debug("Hit an old photo (taken %s; last update was %s); stopping.", timestamp, last_update_date)
                break
            
            photo_id = parsers.safeint(photodict["id"])
            license = licenses[photodict["license"]]
            secret = smart_unicode(photodict["secret"])
            _handle_photo(flickr, photo_id, secret, license, timestamp)
            
        page += 1

def fetch_single_flickr_photo(photo_id, flickr_id):
    flickr = FlickrClient(settings.FLICKR_API_KEY)

    licenses = licenses = flickr.photos.licenses.getInfo()
    licenses = dict((l["id"], smart_unicode(l["url"])) for l in licenses["licenses"]["license"])      

    resp = flickr.photos.getInfo(flickr_id=flickr_id, photo_id=photo_id, extras="license,date_taken")
        
    #timestamp = parsers.parsedate(resp["photo"]["dates"]["taken"])
    timestamp = datetime.datetime.now()
    
    photo_id = parsers.safeint(resp["photo"]["id"])
    license = licenses[resp["photo"]["license"]]
    secret = smart_unicode(resp["photo"]["secret"])
    
    _handle_photo(flickr, photo_id, secret, license, timestamp)
    return Photo.objects.latest() #FIXME: concurrency problem
    
def fetch_single_flickr_photo_with_geo(photo_id, flickr_id, geometry):
    flickr = FlickrClient(settings.FLICKR_API_KEY)

    licenses = licenses = flickr.photos.licenses.getInfo()
    licenses = dict((l["id"], smart_unicode(l["url"])) for l in licenses["licenses"]["license"])      

    resp = flickr.photos.getInfo(flickr_id=flickr_id, photo_id=photo_id, extras="license,date_taken")
        
    #timestamp = parsers.parsedate(resp["photo"]["dates"]["taken"])
    timestamp = datetime.datetime.now()
        
    photo_id = parsers.safeint(resp["photo"]["id"])
    license = licenses[resp["photo"]["license"]]
    secret = smart_unicode(resp["photo"]["secret"])
    
    _handle_photo_with_geo(flickr, photo_id, secret, license, timestamp, geometry)
    return Photo.objects.latest() #FIXME: concurrency problem

def _handle_photo_with_geo(flickr, photo_id, secret, license, timestamp, geometry):
    info = flickr.photos.getInfo(photo_id=photo_id, secret=secret)["photo"]
    server_id = parsers.safeint(info["server"])
    farm_id = parsers.safeint(info["farm"])
    taken_by = smart_unicode(info["owner"]["username"])
    title = smart_unicode(info["title"]["_content"])
    description = smart_unicode(info["description"]["_content"])
    comment_count = parsers.safeint(info["comments"]["_content"])
    date_uploaded = datetime.datetime.fromtimestamp(parsers.safeint(info["dates"]["posted"]))
    date_lastupdate = datetime.datetime.fromtimestamp(parsers.safeint(info["dates"]["lastupdate"]))
    date_received = datetime.datetime.now()
    try:
        latitude      = float(info["location"]["latitude"])
    except KeyError: 
        latitude      = geometry.x
        
    try:
        longitude     = float(info["location"]["longitude"])
    except KeyError:
        longitude     = geometry.y
    
    try:
        accuracy      = parsers.safeint(info["location"]["accuracy"])
    except KeyError:    
        accuracy      = None
    
    try:
        neighbourhood = smart_unicode(info["location"]["neighbourhood"]["_content"])
    except KeyError:
        neighbourhood = None
        
    photo, created = Photo.objects.get_or_create(
        photo_id      = str(photo_id),
        defaults = dict(
            server_id     = server_id,
            farm_id       = farm_id,
            secret        = secret,
            taken_by      = taken_by,
            cc_license    = license,
            title         = title,
            description   = description,
            comment_count = comment_count,
            date_uploaded = date_uploaded,
            date_received  = date_received,
            latitude      = latitude,
            longitude     = longitude,
            accuracy      = accuracy,
            neighbourhood = neighbourhood,
        )
    )
    if created:
        photo.exif = _convert_exif(flickr.photos.getExif(photo_id=photo_id, secret=secret))
    else:
        photo.server_id     = server_id
        photo.farm_id       = farm_id
        photo.secret        = secret
        photo.taken_by      = taken_by
        photo.cc_license    = license
        photo.title         = title
        photo.description   = description
        photo.comment_count = comment_count
        photo.date_uploaded = date_uploaded
        photo.date_received  = date_received
        photo.latitude      = latitude
        photo.longitude     = longitude
        photo.accuracy      = accuracy
        photo.neighbourhood = neighbourhood
    
    photo.save()
    
    return SharedItem.objects.create_or_update(
        instance = photo, 
        timestamp = date_received,
    )
_handle_photo_with_geo = transaction.commit_on_success(_handle_photo_with_geo)


def _handle_photo(flickr, photo_id, secret, license, timestamp):
    info = flickr.photos.getInfo(photo_id=photo_id, secret=secret)["photo"]
    server_id = parsers.safeint(info["server"])
    farm_id = parsers.safeint(info["farm"])
    taken_by = smart_unicode(info["owner"]["username"])
    title = smart_unicode(info["title"]["_content"])
    description = smart_unicode(info["description"]["_content"])
    comment_count = parsers.safeint(info["comments"]["_content"])
    date_uploaded = datetime.datetime.fromtimestamp(parsers.safeint(info["dates"]["posted"]))
    date_lastupdate = datetime.datetime.fromtimestamp(parsers.safeint(info["dates"]["lastupdate"]))
    date_received = datetime.datetime.now()
    try:
        latitude      = float(info["location"]["latitude"])
    except KeyError: 
        latitude      = '42.39873'
        
    try:
        longitude     = float(info["location"]["longitude"])
    except KeyError:
        longitude     = '-71.10764'
    
    try:
        accuracy      = parsers.safeint(info["location"]["accuracy"])
    except KeyError:    
        accuracy      = None
    
    try:
        neighbourhood = smart_unicode(info["location"]["neighbourhood"]["_content"])
    except KeyError:
        neighbourhood = None
        
    log.debug("Handling photo: %r (taken %s)" % (title, timestamp))
    photo, created = Photo.objects.get_or_create(
        photo_id      = str(photo_id),
        defaults = dict(
            server_id     = server_id,
            farm_id       = farm_id,
            secret        = secret,
            taken_by      = taken_by,
            cc_license    = license,
            title         = title,
            description   = description,
            comment_count = comment_count,
            date_uploaded = date_uploaded,
            date_received  = date_received,
            latitude      = latitude,
            longitude     = longitude,
            accuracy      = accuracy,
            neighbourhood = neighbourhood,
        )
    )
    if created:
        photo.exif = _convert_exif(flickr.photos.getExif(photo_id=photo_id, secret=secret))
    else:
        photo.server_id     = server_id
        photo.farm_id       = farm_id
        photo.secret        = secret
        photo.taken_by      = taken_by
        photo.cc_license    = license
        photo.title         = title
        photo.description   = description
        photo.comment_count = comment_count
        photo.date_uploaded = date_uploaded
        photo.date_received  = date_received
        photo.latitude      = latitude
        photo.longitude     = longitude
        photo.accuracy      = accuracy
        photo.neighbourhood = neighbourhood
    
    photo.save()
    
    return SharedItem.objects.create_or_update(
        instance = photo, 
        timestamp = date_received,
    )
_handle_photo = transaction.commit_on_success(_handle_photo)

def _convert_exif(exif):
    converted = {}
    for e in exif["photo"]["exif"]:
        key = smart_unicode(e["label"])
        val = e.get("clean", e["raw"])["_content"]
        val = smart_unicode(val)
        converted[key] = val
    return converted

def _convert_tags(tags):
    return " ".join(set(t["_content"] for t in tags["tag"] if not t["machine_tag"]))
