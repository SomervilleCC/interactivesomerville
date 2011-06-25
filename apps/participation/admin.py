from participation.models import Station, Line
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

admin.site.register(Station, StationAdmin)
admin.site.register(Line, admin.OSMGeoAdmin)