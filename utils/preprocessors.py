import settings
import logging
import datetime

from urlparse import urlparse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse

from sharing.models import SharedItem
from sharing.forms import SharedForm, SharedFormGET


def process_shares():
    shares = list(SharedItem.objects.all().order_by("-share_date")[:15])
    
    for share in shares:
        if share.content_type.app_label == 'photos':
            if share.content_object.neighbourhood:
                continue
            else:
                share.content_object.neighbourhood = u'Somerville'
            if share.content_object.description:
                continue
            else:
                share.content_object.description = u'Dowloaded from Flickr in the Somerville area.'
    return shares
                