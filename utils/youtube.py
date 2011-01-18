import datetime, time
import logging
import feedparser
from django.conf import settings
from django.db import transaction
from django.utils.encoding import smart_unicode, smart_str
from django.utils.encoding import DjangoUnicodeDecodeError
from sharing.models import SharedItem
from videos.models import VideoSource, Video
from greenline.utils import parsers

TAG_SCHEME = 'http://gdata.youtube.com/schemas/2007/keywords.cat'
FEED_URL = 'http://gdata.youtube.com/feeds/api/users/%s/favorites?v=2&start-index=%s&max-results=%s'
ATOM_NS = 'http://www.w3.org/2005/Atom'
MRSS_NS = 'http://search.yahoo.com/mrss/'

YT_GDATAHOST = 'gdata.youtube.com'
YT_FEEDBASE  = '/feeds/api/'

log = logging.getLogger("greenline.youtube")

#
# Public API
#

def gtime2datetime(gtime):
    """Convert GData date and time to a Python datetime object.
    """
    fmt = '%Y-%m-%dT%H:%M:%S'
    gtime = gtime.split('.')[0]
    return datetime.datetime(*(time.strptime(gtime, fmt)[:7]))
        
def enabled():
    ok = hasattr(settings, "YOUTUBE_USERNAME")
    if not ok:
        log.warn('The Youtube provider is not available because the '
                 'YOUTUBE_USERNAME settings is undefined undefined.')
    return ok

def update():    
    start_index = 1
    max_results = 50
    while True:
        #log.debug("Fetching videos %s - %s" % (start_index, start_index+max_results-1))
        feed = feedparser.parse(FEED_URL % (settings.YOUTUBE_USERNAME, start_index, max_results))
        for entry in feed.entries:            
            if 'link' in entry:
                url = entry.link
            elif 'yt_videoid' in entry:
                url = 'http://www.youtube.com/watch?v=%s' % entry.yt_videoid
            else:
                continue
            if 'summary' in entry:
                description = entry.summary
            else:
                continue
                
            _handle_video(
                author = entry.author,
                video_id = entry.videoid,
                title = entry.title, 
                url = url,
                tags = " ".join(t['term'] for t in entry.tags if t['scheme'] == TAG_SCHEME),
                date_uploaded= datetime.datetime(*entry.published_parsed[:6]),
                date_received = datetime.datetime.now(),
                description = description,
            )
        if len(feed.entries) < max_results:
            #log.debug("Ran out of results; finishing.")
            break
            
        start_index += max_results

        
def fetch_single_youtube_video(video_id):
    """Synchronize a Youtube video based on an id"""

    feed = 'http://' + YT_GDATAHOST + YT_FEEDBASE + 'videos/%s' % video_id
        
    entry = parsers.getxml(feed)
    user_root = entry.findtext('{%s}author/{%s}uri' % (ATOM_NS, ATOM_NS))
    user = parsers.getxml(user_root)
    
    _handle_video(
        author = user.findtext('{%s}id' % ATOM_NS).lstrip('http://'+ YT_GDATAHOST + YT_FEEDBASE + 'users/'),
        video_id = video_id,
        title = entry.findtext('{%s}title' % ATOM_NS),
        url = filter(lambda x: x.attrib['rel'] == 'alternate', entry.findall('{%s}link' % ATOM_NS))[0].attrib['href'],
        tags = '',
        date_uploaded = gtime2datetime(entry.findtext('{%s}published' % ATOM_NS)),
        date_received = datetime.datetime.now(),
        description = entry.findtext('{%s}group/{%s}description' % (MRSS_NS, MRSS_NS)) or '',
    )

def fetch_single_youtube_video_with_geo(video_id, geometry):
    """Synchronize a Youtube video based on an id"""

    feed = 'http://' + YT_GDATAHOST + YT_FEEDBASE + 'videos/%s' % video_id
        
    entry = parsers.getxml(feed)
    user_root = entry.findtext('{%s}author/{%s}uri' % (ATOM_NS, ATOM_NS))
    user = parsers.getxml(user_root)
    
    _handle_video_with_geo(
        author = user.findtext('{%s}id' % ATOM_NS).lstrip('http://'+ YT_GDATAHOST + YT_FEEDBASE + 'users/'),
        video_id = video_id,
        title = entry.findtext('{%s}title' % ATOM_NS),
        url = filter(lambda x: x.attrib['rel'] == 'alternate', entry.findall('{%s}link' % ATOM_NS))[0].attrib['href'],
        tags = '',
        date_uploaded = gtime2datetime(entry.findtext('{%s}published' % ATOM_NS)),
        date_received = datetime.datetime.now(),
        description = entry.findtext('{%s}group/{%s}description' % (MRSS_NS, MRSS_NS)) or '',
        geometry = geometry,
    )
    
#
# Private API
#

@transaction.commit_on_success
def _handle_video(author, video_id, title, url, tags, date_uploaded, date_received, description):
    #log.debug("Handling video: %s" % smart_str(title))
    source = VideoSource.objects.get(name="YouTube")
    
    # YouTube API sometimes returns corrupted titles...
    try:
        title = smart_unicode(title)
    except DjangoUnicodeDecodeError:
        return
        
    vid, created = Video.objects.get_or_create(
        url = url, 
        defaults = {
            'author': author,
            'video_id' : video_id,
            'title': title, 
            'source': source,
            'date_uploaded': date_uploaded,
            'date_received': date_received,
            'description': description,
        }
    )
    if created:
        return SharedItem.objects.create_or_update(
            instance = vid, 
            timestamp = date_received,
            source = __name__,
        )

@transaction.commit_on_success
def _handle_video_with_geo(author, video_id, title, url, tags, date_uploaded, date_received, description, geometry):
    #log.debug("Handling video: %s" % smart_str(title))
    source = VideoSource.objects.get(name="YouTube")
    
    # YouTube API sometimes returns corrupted titles...
    try:
        title = smart_unicode(title)
    except DjangoUnicodeDecodeError:
        return
        
    vid, created = Video.objects.get_or_create(
        url = url, 
        defaults = {
            'author': author,
            'video_id' : video_id,
            'title': title, 
            'source': source,
            'date_uploaded': date_uploaded,
            'date_received': date_received,
            'description': description,
            'geometry' : geometry,
        }
    )
    if created:
        return SharedItem.objects.create_or_update(
            instance = vid, 
            timestamp = date_received,
            source = __name__,
        )