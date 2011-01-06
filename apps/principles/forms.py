from django import forms

from principles.models import Entry
from principles.models import Principle

class PrincipleForm(forms.Form):

    choices = forms.MultipleChoiceField(choices=(('1', 'Choice One'), ('2', 'Choice Two'),), initial=['1'], required=False,)
        
'''
class PrincipleForm(forms.ModelForm):
    
    class Meta:
        model = Entry
        fields = ('title', 'body')
'''