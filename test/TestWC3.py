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


from WC3 import ImportXml, ExportXml, fixAmp, debug, trim, xstr, xint, merge, Date, HumanImpact, Location, EconomicImpact, Impact, Link, Reference, Crisis, CrisisInfo, FullAddress, ContactInfo, OrgInfo, Organization, PersonInfo, Person, exists

# -------
# TestWC3
# -------

class TestWC3 (unittest.TestCase) :
    def test_merge_1 (self) :
        
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
        
        
        
        
        
    def test_merge_2 (self) :
    	
        myMail = FullAddress(address = None,
        				     city = None,
        				     state = None,
        				     country = None,
        				     zip_ = None)
        
       
        myMail.put()
        					
        
        myContact = ContactInfo(Phone = None,
                     email =None,
                     mail = myMail)
                     
        myContact.put()
        
        myLoc = Location(city = None,
                            region = None,
                            country = None,
                            missing = None) 
        myLoc.put()
                           
        
        myInfo = OrgInfo(type_ = None,
                            history = None,
          					contact = myContact,
                            loc = myLoc
                            )
        myInfo.put()
        
        myLink = Link(site = None,
                     title = None,
                     url = "https://www.google.com",
                     description = None)
        myLink.put()
        
        myReference = Reference(primaryimage = myLink.key())
        myReference.images.append(myLink.key())
        myReference.videos.append(myLink.key())
        myReference.socials.append(myLink.key())
        myReference.exts.append(myLink.key())
        
        myReference.put()
        
        
        entity = Organization(key_name = "International_Criminal_Court", 
                        idref = "International_Criminal_Court", 
                        name = "International Criminal Court",
                        info = myInfo,
                        ref = myReference,
                        misc = None,
                        relatedCrises = [],
                        relatedPeople = []
                        )
                        
        
                      
        
        
        tree = ET.ElementTree(file = open("WC2.xml", "r"))
        root = tree.getroot()
        orgs = root.findall("organization")
        for organization in orgs: 
            if organization.find("name").text == "International Criminal Court":
                 merge(entity, organization)
        self.assert_(entity.info.loc.city == "Hague")
        
        
        
        
        
        
        
    def test_merge_3 (self) :
        					
        


        
        myBirthdate = Date(time = None,
        				   day = 0,
        				   month = 0,
        				   year = 0,
        				   misc = None)
        myBirthdate.put()
        				   
                           
        
        myInfo = PersonInfo(type_ = None,
                            birthdate = myBirthdate,
          					nationality = None,
                            biography = None
                            )
        myInfo.put()
        
        myLink = Link(site = None,
                     title = None,
                     url = "https://www.google.com",
                     description = None)
        myLink.put()
        

        myReference = Reference(primaryimage = myLink.key())
        myReference.images.append(myLink.key())
        myReference.videos.append(myLink.key())
        myReference.socials.append(myLink.key())
        myReference.exts.append(myLink.key())
        
        myReference.put()
        
        
        entity = Person(key_name = "Mir_Hossein_Mousavi", 
                        idref = "Mir_Hossein_Mousavi", 
                        name = "Mir Hossein Mousavi",
                        info = myInfo,
                        ref = myReference, #TODO
                        misc = None,
                        relatedCrises = [],
                        relatedOrgs = []
                        )
                        
        
                      
        
        
        tree = ET.ElementTree(file = open("WC2.xml", "r"))
        root = tree.getroot()
        people = root.findall("person")
        for person in people: 
            if person.find("name").text == "Mir Hossein Mousavi":
                 merge(entity, person)
        self.assert_(entity.info.nationality == "Iran")
        
        
        
    
    def test_exists_1 (self) :
        db1 = ImportXml("WC2.xml")
        entity = exists("boo")
        self.assert_(entity == False)
        
        
    def test_exists_2 (self) :
        db1 = ImportXml("WC2.xml")
        entity = exists("Mir Hossein Mousavi")
        self.assert_(entity != False)
    
    def test_exists_3 (self) :
        db1 = ImportXml("WC2.xml")
        entity = exists("Libyan Civil War")
        self.assert_(entity != False)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
