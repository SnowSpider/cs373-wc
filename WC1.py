import wsgiref.handlers
import xml.etree.cElementTree as ET
from google.appengine.ext import webapp
import logging
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class ContactInfo(db.Model):
    phone_number = db.StringProperty()
    email = db.EmailProperty()
    address = db.StringProperty()

class Person(db.Model):
    name = db.StringProperty(required=True)
    kind_ = db.StringProperty()
    location = db.StringProperty()
    history = db.TextProperty() # To allow over 500 characters
    images = db.ListProperty(db.Link)
    videos = db.ListProperty(db.Link)
    social_networks = db.ListProperty(db.Link)
    external_links = db.ListProperty(db.Link)
    related_crises = db.StringListProperty() # Crisis
    related_orgs = db.StringListProperty() # Organization
    
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
    related_crises = db.StringListProperty() # Crisis
    related_people = db.StringListProperty() # Person
    
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
    related_orgs = db.StringListProperty() # Organization
    related_people = db.StringListProperty() # Person

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'

    inFile = open("htmlgoodies/mockup.html", 'r')
    outstr = inFile.read() #"HELLO CAR RAMROD"
    inFile.close()
    imported = []
    ImportXml("WC.xml", imported)
    debug(imported)
    self.response.out.write(outstr)


#Assumes valid xml instance
def ImportXml(filename, imported):
  tree = ET.parse(filename)
  root = tree.getroot()
  debug(root)
  debug("HIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
  people = root.find("people").findall("person")
  debug(people)
  for person in people :
    person_model = Person(name=person.find("name").text)
    debug(person_model)
    debug(person_model.name)
    
    kind_ = person.find("kind")
    if kind_ is not None:
        person_model.kind_ = kind_.text
        debug(person_model.kind_)
        
    location = person.find("location")
    if location is not None:
        person_model.location = location.text
        
    history = person.find("history")
    if history is not None:
        person_model.history = history.text
        
    images = person.find("images")
    if images is not None:
        person_model.images = map(lambda e: db.Link(e.text), images.findall("image"))
    
    videos = person.find("videos")
    if videos is not None:
        person_model.videos = map(lambda e: db.Link(e.text), videos.findall("link"))
    
    social_networks = person.find("social_networks")
    if social_networks is not None:
        person_model.social_networks = map(lambda e: db.Link(e.text), social_networks.findall("link"))
    
    external_links = person.find("external_links")
    if external_links is not None:
      person_model.external_links = map(lambda e: db.Link(e.text), external_links.findall("link"))  
      debug(list(person_model.external_links))

    related_crises = person.find("related_crises")
    if related_crises is not None:
        person_model.related_crises = map(lambda e: e.text, related_crises.findall("crisisRef"))
    
    related_orgs = person.find("related_orgs")
    if related_orgs is not None:
        person_model.related_orgs = map(lambda e: e.text, related_orgs.findall("orgRef"))

    imported.append(person_model)
    
    
    
def debug(msg):
    logging.debug("\n\n" + str(msg) + "\n")

def main():
  application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)
