from django.db.models import get_models, signals
from django.conf import settings
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        # Notifications of stuff I'm doing
        notification.create_notice_type("comment_posted", _("Comment Posted"), _("You have posted a comment"), default=1)
        notification.create_notice_type("comment_replied", _("Comment Replied"), _("You have replied to a comment"), default=1)
        
        # Notifications of stuff that concerns me directly
        notification.create_notice_type("comment_reply_received", _("Reply To Comment Received"), _("You have received a reply to a comment"), default=2)

        # Notifications of stuff from my friends/users I'm following
        notification.create_notice_type("comment_friend_posted", _("Friend Posted Comment"), _("A friend has posted a comment"), default=1)
        notification.create_notice_type("comment_friend_replied", _("Friend Replied To Comment"), _("A friend has replied to a comment"), default=1)

    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"

