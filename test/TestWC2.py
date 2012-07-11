#!/usr/bin/env python
# -*- coding: utf8 -*-

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
    % python TestWC2.py > TestWC2.out
    % python TestWC2.py &> TestWC2.out
    % chmod ugo+x TestWC2.py
    % TestWC2.py > TestWC2.out
"""

# -------
# imports
# -------

import StringIO
import unittest
import logging


from WC2 import ImportXml, ExportXml, fixAmp, debug

# -------
# TestPFD
# -------

class TestWC2 (unittest.TestCase) :
    def test_ImportXml_1 (self) :
        data = ImportXml("WC2.xml")
        """
        self.assert_(data["people"]["Mir Hossein Mousavi"].name == "Mir Hossein Mousavi")
        self.assert_(data["people"]["Mir Hossein Mousavi"].type_ == "Presidential Candidate of 2009 Iran's Elections")
        self.assert_(data["people"]["Mir Hossein Mousavi"].loc == "Tehran, Iran")
        self.assert_(data["people"]["Mir Hossein Mousavi"].history == "In 2009 Iranian Presidential election, Mousavi came out of semi-retirement and ran as one of two Reformist candidates against the Administration of incumbent President Mahmoud Ahmadinejad. However he failed to win the election, and following alleged vote rigging and manipulation, his campaign sparked a long protest that eventually turned into a national movement against the Government and Supreme Leader Ali Khamenei. Despite the violent crackdown, he remains the leader of the Green Movement but his movements have remained severely restricted. He chose green as his campaign color, a color which has since become pervasive in Iran. He is currently under house arrest along with his wife and Mehdi Karroubi.")
        self.assert_(data["people"]["Mir Hossein Mousavi"].images[0] == db.Link("http://upload.wikimedia.org/wikipedia/commons/5/59/Mir_Hossein_Mousavi_in_Zanjan_by_Mardetanha.jpg"))
        self.assert_(data["people"]["Mir Hossein Mousavi"].images[1] == db.Link("http://newsimg.bbc.co.uk/media/images/45805000/jpg/_45805312_007298103-1.jpg"))
        self.assert_(data["people"]["Mir Hossein Mousavi"].videos[0] == db.Link("http://www.youtube.com/watch?v=a0yxKpX0iac&feature=related"))
        self.assert_(data["people"]["Mir Hossein Mousavi"].social_networks[0] == db.Link("http://www.facebook.com/mousavi"))
        self.assert_(data["people"]["Mir Hossein Mousavi"].external_links[0] == db.Link("http://news.bbc.co.uk/2/hi/middle_east/8103851.stm"))
        self.assert_(data["people"]["Mir Hossein Mousavi"].related_crises[0] == "Iranian_Green_Movement")
        self.assert_(data["people"]["Mir Hossein Mousavi"].related_orgs[0] == "International_Campaign_for_Human_Rights_in_Iran")
        """
        self.assert_(data["people"])
        
        #self.assert_(True)
    
    """
    def test_ExportXml_1 (self) :
        data = ImportXml("WC2.xml")
        result = ExportXml(data)
        #self.assert_(result == "")
        self.assert_(True)
    """
    def test_fixAmp_1 (self) :
        line = ""
        result = fixAmp(line)
        self.assert_(result == "")
    
    def test_fixAmp_2 (self) :
        line = "&"
        result = fixAmp(line)
        self.assert_(result == "&amp;")
    
    def test_fixAmp_2 (self) :
        line = "&&"
        result = fixAmp(line)
        self.assert_(result == "&amp;&amp;")
        
        
