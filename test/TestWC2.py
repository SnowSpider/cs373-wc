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


from WC2 import ImportXml, ExportXml, fixAmp, debug, trim, xstr, xint

# -------
# TestPFD
# -------

class TestWC2 (unittest.TestCase) :
    def test_ImportXml_1 (self) :
    
        data = ImportXml("WC2.xml")
       
        #for thing in data:
            #debug(thing.idref + "\n\t" + thing.name + "\n\t" + thing.info.type_)
            #debug(thing.ref.primaryImage.url)
       
        self.assert_(data[0].name == "Libyan Civil War")
        self.assert_(data[0].info.history == "The Libyan civil war also referred to as the Libyan Revolution, was an armed conflict in the North African state of Libya, fought between forces loyal to Colonel Muammar Gaddafi and those seeking to oust his government. The war was preceded by protests in Benghazi beginning on Tuesday, 15 February 2011, which led to clashes with security forces that fired on the crowd. The protests escalated into a rebellion that spread across the country, with the forces opposing Gaddafi establishing an interim governing body, the National Transitional Council.")
        self.assert_(data[0].info.help == None)
        self.assert_(data[0].info.resources == "Medicine, fuel, and food.")
        self.assert_(data[0].info.type_ == "Civil War")
        self.assert_(data[0].info.time.time == None)
        self.assert_(data[0].info.time.day == 15)
        self.assert_(data[0].info.time.month == 2)
        self.assert_(data[0].info.time.year == 2011)
        self.assert_(data[0].info.time.misc == None)
        self.assert_(data[0].info.loc.city == None)
        self.assert_(data[0].info.loc.region == None)
        self.assert_(data[0].info.loc.country == "Libya")
        self.assert_(data[0].info.impact.human.deaths == 30000)
        self.assert_(data[0].info.impact.human.displaced == 0)
        self.assert_(data[0].info.impact.human.injured == 50000)
        self.assert_(data[0].info.impact.human.missing == 4000)
        self.assert_(data[0].info.impact.human.misc == None)
        self.assert_(data[0].info.impact.economic.amount == 0)
        self.assert_(data[0].info.impact.economic.currency == None)
        self.assert_(data[0].info.impact.economic.misc == None)
        self.assert_(data[0].ref.primaryImage.url == "http://www.socialistparty.net/images/stories/libyan%20revolt.jpg")
        self.assert_(db.get(data[0].ref.images[0]).url == "http://fifp.files.wordpress.com/2011/04/2011_middle_east_revolutions_-_libyans_protesting_on_tank.jpg")
        self.assert_(db.get(data[0].ref.images[1]).url == "http://www.flixya.com/files-photo/r/i/m/rimawi-1965850.jpg")
        self.assert_(db.get(data[0].ref.images[2]).url == "http://nimg.sulekha.com/others/original700/libya-2011-2-26-12-20-0.jpg")
        self.assert_(db.get(data[0].ref.videos[0]).url == "http://www.youtube.com/embed/8OzwkCGJlAI")
        self.assert_(db.get(data[0].ref.socials[0]).url == "http://www.facebook.com/Liibyan.Revolution")
        self.assert_(db.get(data[0].ref.socials[1]).url == "http://www.facebook.com/Libyan4Life")
        self.assert_(db.get(data[0].ref.exts[0]).url == "http://www.ntc.gov.ly")
        self.assert_(data[0].misc == None)
        self.assert_(data[0].relatedOrgs[0] == "International_Criminal_Court")
        self.assert_(data[0].relatedPeople[0] == "Mustafa_Abdul_Jalil")
        
        #for thing in data:
        #    db.delete(thing)
        
    def test_ImportXml_2 (self) :
    
        data = ImportXml("WC2.xml")
       
        self.assert_(data[4].idref == "World_Uyghur_Congress")
        self.assert_(data[4].name == "World Uyghur Congress")
        self.assert_(data[4].info.type_ == "International organization of exiled Uyghurs")
        self.assert_(data[4].info.history == "The World Uyghur Congress (WUC) is an international organisation that represents the collective interest of the Uyghur people both in East Turkestan and abroad. The WUC was established on 16 April 2004 in Munich, Germany, after the East Turkestan National Congress and the World Uyghur Youth Congress merged into one united organisation. The main objective of WUC is to promote the right of the Uyghur people to use peaceful, nonviolent, and democratic means to determine the political future of East Turkestan. The WUC is a democratic organisation. All of WUC leadership was democratically elected by the participants from all over the world in the General Assembly. They all serve a three-year term. WUC has close contacts and working relations with most Uyghur organisations in the world that peacefully promote human rights, religious freedom, and democracy for the Uyghur people in East Turkestan.")
        
        self.assert_(data[4].info.contact.phone == "0049 (0) 89 5432 1999")
        self.assert_(data[4].info.contact.email == "contact@uyghurcongress.org")
        self.assert_(data[4].info.contact.mail.address == None)
        self.assert_(data[4].info.contact.mail.city == "Munich")
        self.assert_(data[4].info.contact.mail.state == None)
        self.assert_(data[4].info.contact.mail.country == "Germany")
        self.assert_(data[4].info.contact.mail.zip_ == "80103")
        
        self.assert_(data[4].info.loc.city == "Munich")
        self.assert_(data[4].info.loc.region == None)
        self.assert_(data[4].info.loc.country == "Germany")
        
        self.assert_(data[4].ref.primaryImage.url == "http://tibettruth.files.wordpress.com/2009/07/uyghur_xinjiang_flag.gif")
        self.assert_(db.get(data[4].ref.images[0]).url == "http://nimgs3.s3.amazonaws.com/others/original700/2008-6-25-18-58-51-2d65581f891040c796f7e44fb1dd882f-2d65581f891040c796f7e44fb1dd882f-2.jpg")
        self.assert_(db.get(data[4].ref.videos[0]).url == "http://www.youtube.com/embed/877rMmw-7lA")
        self.assert_(db.get(data[4].ref.videos[1]).url == "http://www.youtube.com/embed/5LNuLzqk00c")
        self.assert_(db.get(data[4].ref.socials[0]).url == "https://twitter.com/#!/UyghurCongress")
        self.assert_(db.get(data[4].ref.exts[0]).url == "http://www.uyghurcongress.org")
        self.assert_(db.get(data[4].ref.exts[1]).url == "http://tibettruth.com/2009/07/07/statement-by-the-world-uyghur-congress")
        
        self.assert_(data[4].misc == None)
        self.assert_(data[4].relatedCrises[0] == "Xinjiang_Riots")
        self.assert_(data[4].relatedPeople[0] == "Rebiya_Kadeer")
        
        #for thing in data:
        #    db.delete(thing)
        
    def test_ImportXml_3 (self) :
        
        data = ImportXml("WC2.xml")
       
        self.assert_(data[8].idref == "Mir_Hossein_Mousavi")
        self.assert_(data[8].name == "Mir Hossein Mousavi")
        self.assert_(data[8].info.type_ == "Presidential Candidate of 2009 Iran's Elections")
        self.assert_(data[8].info.birthdate.time == None)
        self.assert_(data[8].info.birthdate.day == 2)
        self.assert_(data[8].info.birthdate.month == 3)
        self.assert_(data[8].info.birthdate.year == 1942)
        self.assert_(data[8].info.birthdate.misc == None)
        self.assert_(data[8].info.nationality == "Iran")
        self.assert_(data[8].info.biography == "In 2009 Iranian Presidential election, Mousavi came out of semi-retirement and ran as one of two Reformist candidates against the Administration of incumbent President Mahmoud Ahmadinejad. However he failed to win the election, and following alleged vote rigging and manipulation, his campaign sparked a long protest that eventually turned into a national movement against the Government and Supreme Leader Ali Khamenei. Despite the violent crackdown, he remains the leader of the Green Movement but his movements have remained severely restricted. He chose green as his campaign color, a color which has since become pervasive in Iran. He is currently under house arrest along with his wife and Mehdi Karroubi.")
        
        self.assert_(data[8].ref.primaryImage.url == "http://upload.wikimedia.org/wikipedia/commons/5/59/Mir_Hossein_Mousavi_in_Zanjan_by_Mardetanha.jpg")
        self.assert_(db.get(data[8].ref.images[0]).url == "http://newsimg.bbc.co.uk/media/images/45805000/jpg/_45805312_007298103-1.jpg")
        self.assert_(db.get(data[8].ref.videos[0]).url == "http://www.youtube.com/embed/a0yxKpX0iac")
        self.assert_(db.get(data[8].ref.socials[0]).url == "http://www.facebook.com/mousavi")
        self.assert_(db.get(data[8].ref.exts[0]).url == "http://news.bbc.co.uk/2/hi/middle_east/8103851.stm")
        
        self.assert_(data[8].misc == None)
        self.assert_(data[8].relatedCrises[0] == "Iranian_Green_Movement")
        self.assert_(data[8].relatedOrgs[0] == "International_Campaign_for_Human_Rights_in_Iran")
        
        #for thing in data:
        #    db.delete(thing)
        
    def test_ExportXml_1 (self) :
        data = ImportXml("test.xml")
        result = ExportXml(data)
        self.assert_(result == "<worldCrises>\n</worldCrises>")
        
        #for thing in data:
        #    db.delete(thing)
        
    def test_ExportXml_2 (self) :
        dataA = ImportXml("WC2.xml")
        resultA = ExportXml(dataA)
        dataB = ImportXml("TestWC2_out.xml")
        resultB = ExportXml(dataB)
        self.assert_(resultA == resultB)
        
        #for thing in dataA:
        #    db.delete(thing)
        #for thing in dataB:
        #    db.delete(thing)
    
    def test_ExportXml_3 (self) :
        dataA = ImportXml("WC2.xml")
        resultA = ExportXml(dataA)
        dataB = ImportXml("WC2.xml")
        resultB = ExportXml(dataB)
        self.assert_(resultA == resultB)
        
        #for thing in dataA:
        #    db.delete(thing)
        #for thing in dataB:
        #    db.delete(thing)
        
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
    
    def test_xstr_1 (self) : 
        tree = ET.ElementTree(file = "WC2.xml")
        root = tree.getroot()
        crises = root.findall("crisis")
        type_ = xstr(crises[0].find("info").find("type"))
        self.assert_(type_ == "Civil War")
    
    def test_xstr_2 (self) : 
        tree = ET.ElementTree(file = "WC2.xml")
        root = tree.getroot()
        crises = root.findall("crisis")
        time = xstr(crises[0].find("info").find("time").find("time"))
        self.assert_(time == None)
    
    def test_xstr_3 (self) : 
        tree = ET.ElementTree(file = "WC2.xml")
        root = tree.getroot()
        crises = root.findall("crisis")
        day = xstr(crises[0].find("info").find("time").find("day"))
        self.assert_(day == "15")
    
    def test_xint_1 (self) : 
        tree = ET.ElementTree(file = "WC2.xml")
        root = tree.getroot()
        crises = root.findall("crisis")
        day = xint(crises[0].find("info").find("time").find("day"))
        self.assert_(day == 15)
        
    def test_xint_2 (self) : 
        tree = ET.ElementTree(file = "WC2.xml")
        root = tree.getroot()
        crises = root.findall("crisis")
        time = xint(crises[0].find("info").find("time").find("time"))
        self.assert_(time == 0)

    def test_xint_3 (self) : 
        tree = ET.ElementTree(file = "WC2.xml")
        root = tree.getroot()
        people = root.findall("person")
        day = xint(people[3].find("info").find("birthdate").find("day"))
        self.assert_(day == 25)

    def test_trim_1 (self) : 
        mystring = ""
        result = trim(mystring)
        self.assert_(result == "")
    
    def test_trim_2 (self) : 
        result = trim(None)
        self.assert_(result == "")
        
    def test_trim_3 (self) : 
        mystring = "I hate M&M"
        result = trim(mystring)
        self.assert_(result == "I hate M&amp;M")
    
    
    
    
