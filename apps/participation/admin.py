from participation.models import Station, Line, Theme, Shareditem, Idea, Meetingnote, Newsarticle, Media, Communitymeeting, Checkin
from django.contrib.gis import admin


# default GeoAdmin overloads
admin.GeoModelAdmin.default_lon = -7915039
admin.GeoModelAdmin.default_lat = 5220376
admin.GeoModelAdmin.default_zoom = 13

 
class StationAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None, 
		{'fields': ['name', 'slug', 'desc', ]}),
		('Map',
		{'fields': ['geometry']}),
	]
	list_display = ('name',)
	search_fields = ('name', 'desc',)
	prepopulated_fields = {'slug': ('name',)}

class ThemeAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, 
		{'fields': ['title', 'slug', 'desc', ]}),
	]
	list_display = ('title',)
	search_fields = ('title', 'desc',)
	prepopulated_fields = {'slug': ('title',)}

class ShareditemAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None,
		{'fields': ['desc', 'itemtype']}),
		('Map',
		{'fields': ['geometry']}),
		('Relations',
		{'fields': ['author', 'station', 'theme',]}),
		('Meta',
		{'fields': ['ip',]}),
	]
	list_display = ('id', 'itemtype', 'station', 'theme',)
	list_filter = ['itemtype', 'station', 'theme',]
	date_hierarchy = 'last_modified'
	search_fields = ('desc',)

class IdeaAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None,
		{'fields': ['desc',]}),
		('Map',
		{'fields': ['geometry']}),
		('Relations',
		{'fields': ['author', 'station', 'theme',]}),
		('Meta',
		{'fields': ['ip',]}),
	]
	list_display = ('id', 'station', 'theme',)
	list_filter = ['station', 'theme',]
	date_hierarchy = 'last_modified'
	search_fields = ('desc',)
	
class MeetingnoteAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None,
		{'fields': ['desc', 'meeting_date', 'note_file', 'note_url', ]}),
		('Map',
		{'fields': ['geometry']}),
		('Relations',
		{'fields': ['author', 'station', 'theme',]}),
		('Meta',
		{'fields': ['ip',]}),
	]
	list_display = ('id', 'station', 'theme',)
	list_filter = ['station', 'theme',]
	date_hierarchy = 'last_modified'
	search_fields = ('desc',)
	
class NewsarticleAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None,
		{'fields': ['desc', 'url', ]}),
		('Map',
		{'fields': ['geometry']}),
		('Relations',
		{'fields': ['author', 'station', 'theme',]}),
		('Meta',
		{'fields': ['ip',]}),
	]
	list_display = ('id', 'station', 'theme',)
	list_filter = ['station', 'theme',]
	date_hierarchy = 'last_modified'
	search_fields = ('desc',)
	
class MediaAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None,
		{'fields': ['desc', 'url', ]}),
		('Map',
		{'fields': ['geometry']}),
		('Relations',
		{'fields': ['author', 'station', 'theme',]}),
		('Meta',
		{'fields': ['ip',]}),
	]
	list_display = ('id', 'station', 'theme',)
	list_filter = ['station', 'theme',]
	date_hierarchy = 'last_modified'
	search_fields = ('desc',)

class CommunitymeetingAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None,
		{'fields': ['title', 'slug', 'date', 'desc', ]}),
		('Meeting Location or Address',
		{'fields': ['geometry', 'location_address', ]}),
	]
	list_display = ('id', 'title', 'location_address', 'date',)
	list_editable = ('title', 'location_address', 'date', )
	date_hierarchy = 'date'
	search_fields = ('title', 'desc',)
	prepopulated_fields = {'slug': ('title',)}

class CheckinAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None,
		{'fields': ['communitymeeting', 'existing_user', ]}),
		('Home Location or Station Area',
		{'fields': ['geometry', 'station', ]}),
	]
	list_display = ('id', 'communitymeeting', 'existing_user', 'station', )
	list_filter = ['station', 'communitymeeting', ]

admin.site.register(Station, StationAdmin)
admin.site.register(Line, admin.OSMGeoAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Shareditem, ShareditemAdmin)
admin.site.register(Idea, IdeaAdmin)
admin.site.register(Meetingnote, MeetingnoteAdmin)
admin.site.register(Newsarticle, NewsarticleAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Communitymeeting, CommunitymeetingAdmin)
admin.site.register(Checkin, CheckinAdmin)