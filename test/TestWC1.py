#!/usr/bin/env python

import unittest
import wsgiref.handlers
import xml.etree.cElementTree as ET
from google.appengine.ext import webapp
import logging
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.ext import testbed
import django.utils.simplejson

"""
To test the program:
    % python TestWC1.py > TestWC1.out
    % python TestWC1.py &> TestWC1.out
    % chmod ugo+x TestWC1.py
    % TestWC1.py > TestWC1.out
"""

# -------
# imports
# -------

import StringIO
import unittest

from WC1 import ImportXml

# -------
# TestPFD
# -------

class TestPFD (unittest.TestCase) :
    
    def test_ImportXml_1 (self) :
        imported = []
        a = ImportXml("WC.xml", imported)
        self.assert_(imported == [])
    
    def test_ImportXml_2 (self) :
        imported = []
        a = ImportXml("WC.xml", imported)
        self.assert_(imported == [])
    
    def test_ImportXml_3 (self) :
        imported = []
        a = ImportXml("WC.xml", imported)
        self.assert_(imported == [])


# ----
# main
# ----

# print "TestWC1.py"
unittest.main()
# print "Done."
