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
import logging


from WC1 import ImportXml, ExportXml, debug

# -------
# TestPFD
# -------

class TestWC1 (unittest.TestCase) :
    
    def test_ImportXml_1 (self) :
        imported = ImportXml("test1.xml")
        self.assert_(imported != {})
        #self.assert_(imported == {"crises":{}, "orgs":{}, "people":{}})
        #self.assert_(True)
        
    def test_ImportXml_2 (self) :
        a = ImportXml("test1.xml")
        b = ImportXml("test1.xml")
        self.assert_(a == b)
        #self.assert_(not any(map(lambda x: True, (k for k in b if k not in a)))) #compares 2 dictionaries by content
    
    def test_ImportXml_3 (self) :
        imported = ImportXml("test2.xml")
        self.assert_(imported["people"]["Sogol"].name == "Sogol")
        self.assert_(imported["crises"]["Migraine"].name == "Migraine")
        self.assert_(imported["orgs"]["UT"].name == "UT")
    
    def test_ImportXml_4 (self) :
        imported = ImportXml("WC.xml")
        self.assert_(imported["people"]["Mir Hossein Mousavi"].name == "Mir Hossein Mousavi")
        self.assert_(imported["people"]["Mir Hossein Mousavi"].kind_ == "Presidential Candidate of 2009 Iran's Elections")
        self.assert_(imported["people"]["Mir Hossein Mousavi"].location == "Tehran, Iran")
        self.assert_(imported["people"]["Mir Hossein Mousavi"].history == "In 2009 Iranian Presidential election, Mousavi came out of semi-retirement and ran as one of two Reformist candidates against the Administration of incumbent President Mahmoud Ahmadinejad. However he failed to win the election, and following alleged vote rigging and manipulation, his campaign sparked a long protest that eventually turned into a national movement against the Government and Supreme Leader Ali Khamenei. Despite the violent crackdown, he remains the leader of the Green Movement but his movements have remained severely restricted. He chose green as his campaign color, a color which has since become pervasive in Iran. He is currently under house arrest along with his wife and Mehdi Karroubi.")
        self.assert_(imported["people"]["Mir Hossein Mousavi"].images[0] == db.Link("http://upload.wikimedia.org/wikipedia/commons/5/59/Mir_Hossein_Mousavi_in_Zanjan_by_Mardetanha.jpg"))
        self.assert_(imported["people"]["Mir Hossein Mousavi"].images[1] == db.Link("http://newsimg.bbc.co.uk/media/images/45805000/jpg/_45805312_007298103-1.jpg"))
        self.assert_(imported["people"]["Mir Hossein Mousavi"].videos[0] == db.Link("http://www.youtube.com/watch?v=a0yxKpX0iac&feature=related"))
        self.assert_(imported["people"]["Mir Hossein Mousavi"].social_networks[0] == db.Link("http://www.facebook.com/mousavi"))
        self.assert_(imported["people"]["Mir Hossein Mousavi"].external_links[0] == db.Link("http://news.bbc.co.uk/2/hi/middle_east/8103851.stm"))
        self.assert_(imported["people"]["Mir Hossein Mousavi"].related_crises[0] == "Iranian_Green_Movement")
        self.assert_(imported["people"]["Mir Hossein Mousavi"].related_orgs[0] == "International_Campaign_for_Human_Rights_in_Iran")
    
    def test_ImportXml_5 (self) :
        imported = ImportXml("WC.xml")
        self.assert_(imported["crises"]["Iranian Green Movement"].name == "Iranian Green Movement")
        self.assert_(imported["crises"]["Iranian Green Movement"].kind_ == "Uprising")
        self.assert_(imported["crises"]["Iranian Green Movement"].location == "Iran")
        self.assert_(imported["crises"]["Iranian Green Movement"].date_and_time == "May 2009")
        self.assert_(imported["crises"]["Iranian Green Movement"].human_impact == "In the aftermath of the election, protests were widened and several massive protests were held around the country by the people. The government arrested a large number of the protesters and several were killed by the police and governmental militia forces. Handala, coming and watching the Iranian Green Movement, has become a web mascot. Although the Iranian government prohibited any form of gathering by opposition-supporters in Tehran and across the country, significantly slowed down internet access and censored any form of media agreeing with the opposition, hundreds of thousands of Iranians chanted this motto, defying the law and challenging the Islamic Republic.")
        self.assert_(imported["crises"]["Iranian Green Movement"].economic_impact == None)
        self.assert_(imported["crises"]["Iranian Green Movement"].resources_needed == "World Support")
        self.assert_(imported["crises"]["Iranian Green Movement"].ways_to_help == "Oppose a Military Strike on Iran, Call for the Release of Opposition Leaders Under House Arrest, Call for the release of imprisoned human rights lawyer Nasrin Sotoudeh!")
        self.assert_(imported["crises"]["Iranian Green Movement"].history == "Protests following the 2009 Iranian presidential election against the disputed victory of Iranian President Mahmoud Ahmadinejad and in support of opposition candidates Mir-Hossein Mousavi and Mehdi Karroubi occurred in major cities in Iran and around the world starting 13 June 2009. The protests were given several titles by their proponents including Green Revolution, Green Wave or Sea of Green, reflecting presidential candidate Mousavi\'s campaign color, and also Persian Awakening. The creation of the Iranian Green Movement was developed during these protests. The events have also been nicknamed the \"Twitter Revolution\" because of the protesters\' reliance on Twitter and other social-networking Internet sites to communicate with each other. Islamic politician Ata\'ollah Mohajerani blasted the election as \"the end of the Islamic Republic\". In response to the protests, other groups rallied in Tehran to support Ahmadinejad.\nWidespread editorial analyses assert that the 2009 election marks the official end of the Islamic Republic and the beginning of the Islamic emirate or an imamate regime. All three opposition candidates claimed that the votes were manipulated and the election was rigged, and candidates Mohsen Rezaee and Mousavi have lodged official complaints. Mousavi announced that he \"won\'t surrender to this manipulation\" before lodging an official appeal against the result to the Guardian Council on 14 June. Ayatollah Ali Khamenei declared the unprecedented voter turnout and coinciding religious holidays as a \"divine assessment\" and urged the nation to unite, but later ostensibly ordered an investigation into the claims of voting fraud and irregularities as per the request of the Green movement leaders. Mousavi is not optimistic about his appeal, saying that many of the group\'s members \"during the election were not impartial\". Ahmadinejad called the election \"completely free\" and the outcome \"a great victory\" for Iran, dismissing the protests as little more than \"passions after a soccer match\".\nPolice and the Basij (a paramilitary group) suppressed both peaceful demonstrating and rioting by using batons, pepper spray, sticks and, in some cases, firearms. The Iranian government has confirmed the deaths of 36 people during the protests, while unconfirmed reports by supporters of Mousavi allege that there have been 72 deaths (twice as many) in the three months following the disputed election. Iranian authorities have closed universities in Tehran, blocked web sites, blocked cell phone transmissions and text messaging, and banned rallies.")
        self.assert_(imported["crises"]["Iranian Green Movement"].images[0] == db.Link("http://upload.wikimedia.org/wikipedia/commons/thumb/6/66/6th_Day_-_Mousavi_inside_the_Crowd.jpg/800px-6th_Day_-_Mousavi_inside_the_Crowd.jpg"))
        self.assert_(imported["crises"]["Iranian Green Movement"].videos[0] == db.Link("http://www.youtube.com/watch?v=quPXg_GoTOk&feature=related"))
        self.assert_(imported["crises"]["Iranian Green Movement"].social_networks[0] == db.Link("http://www.facebook.com/Persian.Green.Movement"))
        self.assert_(imported["crises"]["Iranian Green Movement"].external_links[0] == db.Link("http://en.irangreenvoice.com"))
        self.assert_(imported["crises"]["Iranian Green Movement"].related_orgs[0] == "International_Campaign_for_Human_Rights_in_Iran")
        self.assert_(imported["crises"]["Iranian Green Movement"].related_people[0] == "Mir_Hossein_Mousavi")
        
    def test_ImportXml_6 (self) :
        imported = ImportXml("WC.xml")
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].name == "International Campaign for Human Rights in Iran")
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].kind_ == "Campaign")
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].location == "Netherlands")
        
        # history
        # Non-ASCII character '\xe2' in file
        """
        debug(imported["orgs"]["International Campaign for Human Rights in Iran"].contact_info.email)
        debug(imported["orgs"]["International Campaign for Human Rights in Iran"].contact_info.phone_number)
        debug(imported["orgs"]["International Campaign for Human Rights in Iran"].contact_info.address)
        """
        
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].contact_info.email == db.Email("info@iranhumanrights.org"))
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].contact_info.phone_number == db.PhoneNumber("0000000"))
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].contact_info.address == db.PostalAddress("Netherlands"))
        
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].images[0] == db.Link("http://www.iranhumanrights.org/wp-content/uploads/Ronaghi21-300x2171.jpg"))
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].videos[0] == db.Link("http://www.youtube.com/watch?v=B-Kmb1Hm0n0&feature=player_embedded"))
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].social_networks[0] == db.Link("http://www.facebook.com/pages/International-Campaign-for-Human-Rights-in-Iran/49929580840"))
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].external_links[0] == db.Link("http://www.iranhumanrights.org"))
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].related_crises[0] == "Iranian_Green_Movement")
        self.assert_(imported["orgs"]["International Campaign for Human Rights in Iran"].related_people[0] == "Mir_Hossein_Mousavi")
    
    def test_ExportXml_1 (self) :
        data = ImportXml("WC.xml")
        ExportXml(data)
        self.assert_(True)
    
    
        
