# -*- coding: utf-8 -*-
import re

from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag("ideas/idea_item.html")
def show_idea_post(idea_post):
    return {"idea_post": idea_post}
