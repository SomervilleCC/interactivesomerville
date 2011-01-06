from datetime import datetime
from django import forms

from ideas.models import Idea

class IdeaForm(forms.ModelForm):
    
    class Meta:
        model = Idea
        exclude = ('author', 'creator_ip', 'created', 'publish', 'geometry', 'slug', )
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(IdeaForm, self).__init__(*args, **kwargs)
    
    def clean_slug(self):
        if not self.instance.pk:
            if Idea.objects.filter(author=self.user, created__month=datetime.now().month, created__year=datetime.now().year, slug=self.cleaned_data['slug']).count():
                raise forms.ValidationError(u'This field must be unique for username, year, and month')
            return self.cleaned_data['slug']
        try:
            idea = Idea.objects.get(author=self.user, created__month=self.instance.created_at.month, created__year=self.instance.created.year, slug=self.cleaned_data['slug'])
            if idea != self.instance:
                raise forms.ValidationError(u'This field must be unique for username, year, and month')
        except Idea.DoesNotExist:
            pass
        return self.cleaned_data['slug']
        

