import datetime
from django import forms
from location.models import Location

class LocationForm(forms.ModelForm):

    class Meta:
        model = Location
        exclude = ('author', 'slug', 'geometry', 'station', 'created', 'title', )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(LocationForm, self).__init__(*args, **kwargs)