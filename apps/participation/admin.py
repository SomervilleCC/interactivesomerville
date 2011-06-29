from participation.models import Station, Line, Theme, Idea, Meetingnote
from django.contrib.gis import admin

class StationAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None, 
		{"fields": ["name", "slug", "desc", ]}),
		("Map",
		{"fields": ["geometry"]}),
	]
	list_display = ("name",)
	search_fields = ("name", "desc",)
	prepopulated_fields = {"slug": ("name",)}

class ThemeAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, 
		{"fields": ["title", "slug", "desc", ]}),
	]
	list_display = ("title",)
	search_fields = ("title", "desc",)
	prepopulated_fields = {"slug": ("title",)}

class IdeaAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None,
		{"fields": ["desc"]}),
		("Map",
		{"fields": ["geometry"]}),
		("Relations",
		{"fields": ["author", "station", "theme",]}),
		("Meta",
		{"fields": ["ip",]}),
	]
	list_display = ("id", "station", "theme",)
	list_filter = ["station", "theme",]
	date_hierarchy = "last_modified"
	search_fields = ("desc",)
	
class MeetingnoteAdmin(admin.OSMGeoAdmin):
	fieldsets = [
		(None,
		{"fields": ["desc", "meeting_date", "note_file", "note_url"]}),
		("Map",
		{"fields": ["geometry"]}),
		("Relations",
		{"fields": ["author", "station", "theme",]}),
		("Meta",
		{"fields": ["ip",]}),
	]
	list_display = ("id", "station", "theme",)
	list_filter = ["station", "theme",]
	date_hierarchy = "last_modified"
	search_fields = ("desc",)

admin.site.register(Station, StationAdmin)
admin.site.register(Line, admin.OSMGeoAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Idea, IdeaAdmin)
admin.site.register(Meetingnote, MeetingnoteAdmin)