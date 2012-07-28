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


from WC3 import ImportXml, ExportXml, fixAmp, debug, trim, xstr, xint, merge, Date, HumanImpact, Location, EconomicImpact, Impact, Link, Reference, Crisis, CrisisInfo

# -------
# TestWC3
# -------

class TestWC3 (unittest.TestCase) :
    def test_ImportXml_1 (self) :
        
        myTime = Date(time = None,
                      day = 0,
                      month = 0,
                      year = 0, 
                      misc = None)
        myTime.put()
        
        myLoc = Location(city = None,
                            region = None,
                            country = None,
                            missing = None) 
        myLoc.put()
                            
        myHuman = HumanImpact(deaths = 0,
                            displaced = 0,
                            injured = 0,
                            missing = 0, 
                            misc = None)
        myHuman.put()
                            
        myEconomic = EconomicImpact(amount = 0,
                                    currency = None,
                                    misc = None)
        myEconomic.put()
        
        myImpact = Impact(human = myHuman,
                          economic = myEconomic)
        myImpact.put()
        
        myInfo = CrisisInfo(history = None,
                            help = None,
                            resources = None,
                            type_ = None, 
                            time = myTime,
                            loc = myLoc,
                            impact = myImpact
                            )
        myInfo.put()
        
        myLink = Link(site = None,
                     title = None,
                     url = "https://www.google.com", #TODO
                     description = None)
        myLink.put()
        
        myReference = Reference(primaryimage = myLink.key())
        myReference.images.append(myLink.key())
        myReference.videos.append(myLink.key())
        myReference.socials.append(myLink.key())
        myReference.exts.append(myLink.key())
        
        myReference.put()
        
        
        entity = Crisis(key_name = "Libyan_Civil_War", 
                        idref = "Libyan_Civil_War", 
                        name = "Libyan Civil War",
                        info = myInfo,
                        ref = myReference,
                        misc = None,
                        relatedOrgs = [],
                        relatedPeople = []
                        )
                        
        
                      
        
        
        tree = ET.ElementTree(file = open("WC2.xml", "r"))
        root = tree.getroot()
        crises = root.findall("crisis")
        for crisis in crises: 
            if crisis.find("name").text == "Libyan Civil War":
                 merge(entity, crisis)
        self.assert_(entity.info.time.year == 2011)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
