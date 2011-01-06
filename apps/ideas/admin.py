from ideas.models import Idea
from django.contrib import admin

class IdeaAdmin(admin.ModelAdmin):
    list_display        = ('title', 'publish', 'public')
    list_filter         = ('publish', 'public')
    search_fields       = ('title', 'description', 'tease')

admin.site.register(Idea, IdeaAdmin)