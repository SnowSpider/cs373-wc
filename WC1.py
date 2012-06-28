import wsgiref.handlers
import xml.etree.cElementTree as ET
from google.appengine.ext import webapp
import logging
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class ContactInfo(db.Model):
    phone_number = PhoneNumberProperty
    email = EmailProperty()
    address = PostalAddressProperty()

class Person(db.Model):
    name = db.StringProperty(required=True)
    kind = db.StringProperty()
    location = db.StringProperty()
    history = db.StringProperty()
    images = db.ListProperty(db.Link)
    videos = db.ListProperty(db.Link)
    social_networks = db.ListProperty(db.Link)
    external_links = db.ListProperty(db.Link)
    related_crises = db.ListProperty(str)
    related_orgs = db.ListProperty(str)
    
class Organization(db.Model):
    name = db.StringProperty(required=True)
    kind = db.StringProperty()
    location = db.StringProperty()
    history = db.StringProperty()
    contact_info = ContactInfo()
    images = db.ListProperty(db.Link)
    videos = db.ListProperty(db.Link)
    social_networks = db.ListProperty(db.Link)
    external_links = db.ListProperty(db.Link)
    related_crises = db.ListProperty(str)
    related_people = db.ListProperty(str)
    
class Crisis(db.Model):
    name = db.StringProperty(required=True)
    kind = db.StringProperty()
    location = db.StringProperty()
    date_and_time = db.StringProperty()
    human_impact = db.StringProperty()
    economic_impact = db.StringProperty()
    resources_needed = db.StringProperty()
    ways_to_help = db.StringProperty()
    history = db.StringProperty()
    images = db.ListProperty(db.Link)
    videos = db.ListProperty(db.Link)
    social_networks = db.ListProperty(db.Link)
    external_links = db.ListProperty(db.Link)
    related_orgs = db.ListProperty(str)
    related_people = db.ListProperty(str)

class Everything(db.Model):
    people = db.ListProperty(Person)
    crises = db.ListProperty(Crisis)
    organizations = db.ListProperty(Organization)

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'

    inFile = open("htmlgoodies/mockup.html", 'r')
    outstr = inFile.read() #"HELLO CAR RAMROD"
    inFile.close()
    ImportXml("WC.xml")
    self.response.out.write(outstr)


#Assumes valid xml instance
def ImportXml(filename):
  tree = ET.parse(filename)
  root = tree.getroot()
  logging.debug(root)
  logging.debug("HIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
  people = root.find("people").findall("person")
  logging.debug(people)
  for person in people :
    person_model = Person()
    person_model.name = person.find("name")

def main():
  
  application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)
