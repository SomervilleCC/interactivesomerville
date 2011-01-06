ALLDIRS = ['/home/gmccollam/.virtualenvs/pinax-073/lib/python2.6/site-packages']
# note that the above directory depends on the locale of your virtualenv,
# and will thus be *different for each project!*
import os
import sys
import site
from os.path import abspath, dirname, join
sys.stdout = sys.stderr

prev_sys_path = list(sys.path)

for directory in ALLDIRS:
    site.addsitedir(directory)

new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
       new_sys_path.append(item)
       sys.path.remove(item)
sys.path[:0] = new_sys_path

# this will also be different for each project!
sys.path.insert(0, '/home/gmccollam/greenline/')

from django.conf import settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../'))
sys.path.insert(0, root_path)
sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

