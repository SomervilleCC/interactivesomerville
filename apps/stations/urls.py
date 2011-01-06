from django.conf.urls.defaults import *
from stations import views as station_views
from stations.forms import StationForm


urlpatterns = patterns('',
    url(r'^$', view=station_views.stations, name='stations'),
    url(r'^your_station/$', view=station_views.your_station, name='your_station'),
    (r'^validate/$', 'ajax_validation.views.validate', {'form_class': StationForm, 'callback': lambda request, *args, **kwargs: {'user': request.user}}, 'station_form_validate'),
)