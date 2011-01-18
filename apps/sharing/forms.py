import datetime
from django import forms
from django.utils.encoding import force_unicode
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from sharing.models import SharedItem
from greenline.utils import flickr

from django import forms
from uni_form.helpers import FormHelper, Submit, Reset
from sharing.models import SharedItem
from django.forms import ModelForm

import logging

log = logging.getLogger("greenline.sharing.forms")
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.INFO)

PRINCIPLE_CHOICES = ( \
    (1, 'More Local Jobs'), \
    (2, 'Economic Development'), \
    (3, 'Keep and Add Local Businesses'), \
    (4, 'Keep Somerville Affordable'), \
    (5, 'Maintain Our Diversity'), \
    (6, 'Improve the Green Environment'), \
    (7, 'Encourage Walking and Biking'), \
    (8, 'Create Community Gathering Spaces'), \
    (9, 'Improve Access'), \
    (10, 'Community Involvement'), \
    (11, 'Connecting Buses and Trains'))


class SharedFormGET(forms.Form):
    
    location = forms.CharField(widget=forms.TextInput(attrs={'size':28}), required=True )
    media_type = forms.URLField(widget=forms.TextInput(attrs={'size':28}), required=False )
    related_principle = forms.MultipleChoiceField(choices=PRINCIPLE_CHOICES, initial=['1'], required=False)
    comment = forms.CharField(label="Comment", widget=forms.widgets.Textarea())
    
    content_type    = forms.CharField(widget=forms.HiddenInput, initial='content_type')
    object_id       = forms.CharField(widget=forms.HiddenInput, initial='object_id')
    
class SharedForm(forms.ModelForm):

    content_type    = forms.CharField(widget=forms.HiddenInput, initial='content_type')
    object_id       = forms.CharField(widget=forms.HiddenInput, initial='object_id')
    
    class Meta:
        model = SharedItem
        exclude = ('user', 'share_date', 'content_type', 'object_id', 'tags')

    def __init__(self, target_object, user=None, data=None, initial=None):
        self.user = user
        self.target_object = target_object

        if initial is None:
            initial = {}
        initial.update(self.generate_object_data())
        super(SharedForm, self).__init__(data=data, initial=initial)

    def generate_object_data(self):
        """Generate a dict of security data for "initial" data."""
        object_dict =   {
            'content_type'  : str(self.target_object._meta),
            'object_id'     : str(self.target_object._get_pk_val()),
        }
        return object_dict
        
    def get_shared_object(self):
        """
        Return a new (unsaved) shareditem object.

        Does not set any of the fields that would come from the Request object
        (i.e. ``user``).
        """
        if not self.is_valid():
            raise ValueError("get_shared_object may only be called on valid forms")

        new = SharedItem(
            object_id    = force_unicode(self.target_object._get_pk_val()),
            content_type = ContentType.objects.get_for_model(self.target_object),
            share_date  = datetime.datetime.now(),
        )
        
        return new
    
class SharedItemForm(forms.Form):
    
    title       = forms.CharField(required=False, widget=forms.Textarea,max_length=255)
    media_url   = forms.URLField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 65}))

    content_type    = forms.CharField(widget=forms.HiddenInput, initial='content_type')
    object_id       = forms.CharField(widget=forms.HiddenInput, initial='object_id')

    class Meta:
        model = SharedItem
        exclude = ('user',)

    def __init__(self, target_object, user=None, data=None, initial=None):
        self.user = user
        self.target_object = target_object
        if initial is None:
            initial = {}
        initial.update(self.generate_object_data())

        if initial is None:
            initial = {}
        super(SharedItemForm, self).__init__(data=data, initial=initial)
        
    def generate_object_data(self):
        """Generate a dict of security data for "initial" data."""
        object_dict =   {
            'content_type'  : str(self.target_object._meta),
            'object_id'     : str(self.target_object._get_pk_val()),
        }
        return object_dict

    def get_shared_object(self):
        """
        Return a new (unsaved) shareditem object.

        Does not set any of the fields that would come from the Request object
        (i.e. ``user``).
        """
        if not self.is_valid():
            raise ValueError("get_shared_object may only be called on valid forms")

        new = SharedItem(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_id    = force_unicode(self.target_object._get_pk_val()),
            share_date  = datetime.datetime.now(),
        )
        
        return new

    def clean_content(self):
        pass