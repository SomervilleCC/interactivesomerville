"""
Replace these with more appropriate tests for your application.
"""
import datetime
import unittest
from django.test import TestCase
from django.test.client import Client
import json
from django.contrib.gis.geos import GEOSGeometry, GEOSGeometry, fromstr, fromfile

__test__ = {"doctest": """

>>> pnt = Station.objects.all()
>>> for p in pnt:
    print p.geometry.valid
True
True
True
True
True
True
True

>>> rt = Route.objects.all()
>>> for r in rt:
    print r.geometry.valid
True
True

"""}
