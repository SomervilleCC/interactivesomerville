from django.contrib import admin
from django.conf import settings
from mptt_comments.models import MpttComment
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.models import Comment
from django.contrib.comments.admin import CommentsAdmin
from django.contrib.contenttypes.models import ContentType

class MpttCommentsAdmin(CommentsAdmin):
    fieldsets = (
        (None,
           {'fields': ('content_type', 'object_pk', 'parent', 'site')}
        ),
        (_('Content'),
           {'fields': ('user', 'title', 'comment')}
        ),
        (_('Metadata'),
           {'fields': ('submit_date', 'ip_address', 'is_public', 'is_removed')}
        )
     )

    raw_id_fields = ('parent', 'user') # We don't really want to get huge <select> with all the comments, users...
    list_display = ('title', 'user', 'getobject', 'level', 'ip_address', 'submit_date', 'is_public', 'is_removed')
    list_filter = ('submit_date', 'is_public', 'is_removed')
    date_hierarchy = 'submit_date'
    ordering = ('-submit_date',)
    search_fields = ('comment', 'user__username', 'user_name', 'user_email', 'user_url', 'ip_address')

    def getobject(self, obj):
        try:
            object_type = ContentType.objects.get(model=str(obj.content_type))
            o = object_type.get_object_for_this_type(pk=str(obj.object_pk))
        except:
            o = "%s : %s" % (obj.content_type, obj.object_pk) 
        return o
    getobject.short_description = 'Object'

try:
	admin.site.unregister(Comment)
except:
	pass
admin.site.register(MpttComment, MpttCommentsAdmin)
