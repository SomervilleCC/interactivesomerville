from principles.models import Principle, Entry
from django.contrib import admin

class PrincipleAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    list_display = ('title', 'body',)
    ordering = ('-title',)
        
class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    list_display = ('title', 'body', 'created', 'status',)
    list_filter = ('created', 'status', )
    ordering = ('-created',)
        
admin.site.register(Principle, PrincipleAdmin)
admin.site.register(Entry, EntryAdmin)