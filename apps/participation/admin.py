from participation.models import Station, Line, Theme
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

admin.site.register(Station, StationAdmin)
admin.site.register(Line, admin.OSMGeoAdmin)
admin.site.register(Theme, ThemeAdmin)