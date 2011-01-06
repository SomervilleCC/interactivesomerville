# Creating a HiddenBaseForm. from djangosnippets.org.
# Author : Yashh (www.yashh.com)

from django import forms
from django.forms.forms import BoundField
from location.models import Location

class StationForm(forms.ModelForm):
    
    class Meta:
        model = Location
        exclude = ('author', 'title', 'slug', 'description', 'geometry', 'location_type', 'station', 'created', 'principle', 'tags', )
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(StationForm, self).__init__(*args, **kwargs)