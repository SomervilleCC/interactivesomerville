from django.db import models
from django.utils.translation import ugettext_lazy as _

from idios.models import ProfileBase
from participation.models import Station


class Profile(ProfileBase):
	name = models.CharField(_("name"), max_length=50, null=True, blank=True)
	about = models.TextField(_("about"), null=True, blank=True)
	website = models.URLField(_("website"), null=True, blank=True, verify_exists=False)
	mystation = models.ForeignKey(Station, null=True, blank=True)
	flickr_id = models.CharField("My Flickr username", max_length=50, null=True, blank=True)
	youtube_id = models.CharField("My YouTube username", max_length=50, null=True, blank=True)
	twitter_id = models.CharField("My Twitter username", max_length=50, null=True, blank=True)
	facebook_id = models.CharField("My Facebook username", max_length=50, null=True, blank=True)
