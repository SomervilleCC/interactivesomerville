from django import template

from participation.models import Shareditem

register = template.Library()

def get_user_activities(context):

	activities = Shareditem.objects.filter(author=context['page_user'])[:5].select_subclasses()
	
	return {
		'activities': activities,
	}
	
register.inclusion_tag("profiles/_activities.html", takes_context=True)(get_user_activities)