from django.http import HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.urlresolvers import reverse

from functools import wraps

def login_required_ajax(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        is_ajax = request.POST.get('is_ajax') and '_ajax' or ''
        if is_ajax and not request.user.is_authenticated():
            # User is not authenticated and we are using the ajax version.
            # Instead of using @login_required, which redirects, we send a
            # 403 Forbidden answer directly. 401 would be more appropriate but
            # we are not support WWW-Authenticate header authentification method
            html = _('Please <a href="%(login_url)s">log-in</a> or <a href="%(register_url)s">create an account</a> before proceeding')
            html = html % {
                'login_url': reverse('django.contrib.auth.views.login'),
                'register_url': reverse('registration_register'),
            }
            return HttpResponseForbidden(html)
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view
