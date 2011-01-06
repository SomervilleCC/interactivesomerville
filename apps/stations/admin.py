from stations.models import Station, Route, Radius
from django.contrib.gis import admin

class StationAdmin(admin.ModelAdmin):
    search_fields       = ('name', 'copy',)
    list_display = ('name',)

admin.site.register(Station, StationAdmin)