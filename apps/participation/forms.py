from django.forms import ModelForm, HiddenInput

from greenline.apps.participation.models import Idea

class IdeaForm(ModelForm):
	class Meta:
		model = Idea
		exclude = ("author", "desc_markup_type", "ip", "created", "last_modified",)
		widgets = {
			"geometry": HiddenInput(),
		}