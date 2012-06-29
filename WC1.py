import wsgiref.handlers
import xml.etree.cElementTree as ET
from google.appengine.ext import webapp
import logging
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class ContactInfo(db.Model):
    phone_number = db.PhoneNumberProperty()
    email = db.EmailProperty()
    address = db.PostalAddressProperty()

class Person(db.Model):
    name = db.StringProperty(required=True)
    kind_ = db.StringProperty()
    location = db.StringProperty()
    history = db.TextProperty() # To allow over 500 characters
    images = db.ListProperty(db.Link)
    videos = db.ListProperty(db.Link)
    social_networks = db.ListProperty(db.Link)
    external_links = db.ListProperty(db.Link)
    related_crises = db.ListProperty(str)
    related_orgs = db.ListProperty(str)
    
class Organization(db.Model):
    name = db.StringProperty(required=True)
    kind_ = db.StringProperty()
    location = db.StringProperty()
    history = db.TextProperty() # To allow over 500 characters
    contact_info = ContactInfo()
    images = db.ListProperty(db.Link)
    videos = db.ListProperty(db.Link)
    social_networks = db.ListProperty(db.Link)
    external_links = db.ListProperty(db.Link)
    related_crises = db.ListProperty(str)
    related_people = db.ListProperty(str)
    
class Crisis(db.Model):
    name = db.StringProperty(required=True)
    kind_ = db.StringProperty()
    location = db.StringProperty()
    date_and_time = db.StringProperty()
    human_impact = db.StringProperty()
    economic_impact = db.StringProperty()
    resources_needed = db.StringProperty()
    ways_to_help = db.StringProperty()
    history = db.TextProperty() # To allow over 500 characters
    images = db.ListProperty(db.Link)
    videos = db.ListProperty(db.Link)
    social_networks = db.ListProperty(db.Link)
    external_links = db.ListProperty(db.Link)
    related_orgs = db.ListProperty(str)
    related_people = db.ListProperty(str)

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
  debug(root)
  debug("HIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
  people = root.find("people").findall("person")
  debug(people)
  for person in people :
    person_model = Person(name=person.find("name").text)
    kind_ = person.find("kind")
    if kind_ is not None:
        person_model.kind_ = kind_.text
    location = person.find("location")
    if location is not None:
        person_model.location = location.text
    history = person.find("history")
    if history is not None:
        person_model.history = history.text
        
    images = map(lambda e: e.text, person.find("images").findall("link")) # we should make images required (in both xml and model) to avoid ambiguity. For now this code assumes that images is required.
    videos = map(lambda e: e.text, person.find("videos").findall("link"))
        
def debug(msg):
    logging.debug("\n\n" + str(msg) + "\n")

def main():
  application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)
