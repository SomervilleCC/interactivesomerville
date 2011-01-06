import re
import httplib2
import dateutil.parser
import dateutil.tz
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.conf import settings
from greenline.utils.anyetree import etree

DEFAULT_HTTP_HEADERS = {
    "User-Agent" : "Greenline"
}


# URL fetching 

def getxml(url, **kwargs):
    """Fetch and parse XML. Return an ElementTree"""
    xml = fetch_resource(url, **kwargs)
    return etree.fromstring(xml)
    
def getjson(url, **kwargs):
    """Fetch and parse JSON. Return the deserialized JSON."""
    json = fetch_resource(url, **kwargs)
    return simplejson.loads(json)

def fetch_resource(url, method="GET", body=None, username=None, password=None, headers=None):
    h = httplib2.Http(timeout=15)
    h.force_exception_to_status_code = True
    
    if username is not None or password is not None:
        h.add_credentials(username, password)
    
    if headers is None:
        headers = DEFAULT_HTTP_HEADERS.copy()
    
    response, content = h.request(url, method, body, headers)
    return content

# Date handling utils

def parsedate(s):
    """
    Convert a string into a (local, naive) datetime object.
    """
    dt = dateutil.parser.parse(s)
    if dt.tzinfo:
        dt = dt.astimezone(dateutil.tz.tzlocal()).replace(tzinfo=None)
    return dt

def safeint(s):
    """Always returns an int. Returns 0 on failure."""
    try:
        return int(force_unicode(s))
    except (ValueError, TypeError):
        return 0


GREENLINE_ADJUST_DATETIME = False
if hasattr(settings,'GREENLINE_ADJUST_DATETIME'):
    GREENLINE_ADJUST_DATETIME = settings.GREENLINE_ADJUST_DATETIME

if GREENLINE_ADJUST_DATETIME:
    try:
        import pytz
    except ImportError:
        import logging
        log = logging.getLogger('GREENLINE.providers.utils')
        log.error("Cannot import pytz package and consequently, all datetime objects will be naive. "
                  "In this particular case, e.g., all commit dates will be expressed in UTC.")

    import datetime
    import time

    UTC = pytz.timezone('UTC')
    LOCAL = pytz.timezone(settings.TIME_ZONE)

    def utc_to_local_datetime(dt):
        """
        Map datetime as UTC object to it's localtime counterpart.
        """
        return dt.astimezone(LOCAL)

    def utc_to_local_timestamp(ts, orig_tz=UTC):
        """
        Convert a timestamp object into a tz-aware datetime object.
        """
        timestamp = datetime.datetime.fromtimestamp(ts,tz=orig_tz)
        return timestamp.astimezone(LOCAL)

    def utc_to_local_timestruct(ts, orig_tz=UTC):
        """
        Convert a timestruct object into a tz-aware datetime object.
        """
        return utc_to_local_timestamp(time.mktime(ts),orig_tz)


def slugify(s, num_chars=50): 
    ''' 
    NOTE: this implementation corresponds to the Python implementation 
          of the same algorithm in django/contrib/admin/media/js/urlify.js 
    ''' 
    # remove all these words from the string before urlifying 
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for", 
                  "from", "is", "in", "into", "like", "of", "off", "on", 
                  "onto", "per", "since", "than", "the", "this", "that", 
                  "to", "up", "via", "with"] 
    ignore_words = '|'.join([r for r in removelist]) 
    ignore_words_pat = re.compile('\b('+ignore_words+')\b', re.I) 
    ignore_chars_pat = re.compile(r'[^-A-Z0-9\s]', re.I) 
    outside_space_pat = re.compile(r'^\s+|\s+$') 
    inside_space_pat = re.compile(r'[-\s]+') 

    s = ignore_words_pat.sub('', s)  # remove unimportant words 
    s = ignore_chars_pat.sub('', s)  # remove unneeded chars 
    wordlist = s.split()
    s = ''
    for w in wordlist:
        ns = s + w + ' '
        if len(ns) <= num_chars:
            s = ns
        else:
            break
    s = outside_space_pat.sub('', s) # trim leading/trailing spaces
    s = inside_space_pat.sub('-', s) # convert spaces to hyphens 
    s = s.lower()                    # convert to lowercase 
    return s