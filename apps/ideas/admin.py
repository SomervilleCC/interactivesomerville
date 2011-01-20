from ideas.models import Idea
from django.contrib import admin

class IdeaAdmin(admin.ModelAdmin):
    list_display        = ('title', 'publish', 'share', )
    list_filter         = ('publish', 'share', 'title', )
    search_fields       = ('title', )

admin.site.register(Idea, IdeaAdmin)