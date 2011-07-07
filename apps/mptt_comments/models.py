import datetime
import mptt

from django.db import models
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager
from django.core import urlresolvers

class MpttCommentManager(CommentManager):

    def get_query_set(self):
        return super(MpttCommentManager, self).get_query_set().select_related('user')
    
    def filter_hidden_comments(self):
        """
        Match django's templatetags/comments.py behavior and hide is_public=False
        comments, and is_removed=True comments if COMMENTS_HIDE_REMOVED is True.
         
        We need it because some views (comments_more, comments_subtree...) play 
        with the queryset themselves instead of just using the templatetag  
        """
        # FIXME: We need to do something clever for those hidden comments in order
        #        not to break the displayed tree
        rval = self
        field_names = [f.name for f in self.model._meta.fields]
        if 'is_public' in field_names:
            rval = rval.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True) and 'is_removed' in field_names:
            rval = rval.filter(is_removed=False)
        return rval

class AbstractMpttComment(Comment):

    title = models.CharField(max_length=255)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True)
    
    def save(self, *a, **kw):
        if not self.ip_address:
            self.ip_address = '0.0.0.0'
        super(AbstractMpttComment, self).save(*a, **kw)
        
    def get_absolute_url(self):
        return urlresolvers.reverse(
              "comment-detail",
              args=(self.id, )
          )
    
    class Meta:
        abstract = True
        ordering = ('tree_id', 'lft')

class MpttComment(AbstractMpttComment):
    
    objects = MpttCommentManager()

mptt.register(MpttComment)
