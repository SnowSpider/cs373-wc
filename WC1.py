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
    human_impact = db.TextProperty()
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

  orgs = root.find("orgs").findall("org")
  for org in orgs :
    org_model = Organization(name=org.find("name").text)
    debug(org_model)
    debug(org_model.name)
    
    kind_ = org.find("kind")
    if kind_ is not None:
        org_model.kind_ = kind_.text
        debug(org_model.kind_)
        
    location = org.find("location")
    if location is not None:
        org_model.location = location.text
        
    history = org.find("history")
    if history is not None:
        org_model.history = history.text

    contact_info = org.find("contact_info")
    contact_info_model = ContactInfo()
    email = contact_info.find("email")
    phone_number = contact_info.find("phone_number")
    address = contact_info.find("address")
    if email is not None:
        contact_info_model.email = email.text
    if phone_number is not None:
        contact_info_model.phone_number = phone_number.text
    if address is not None:
        contact_info_model.address = address.text
        
    images = org.find("images")
    if images is not None:
        org_model.images = map(lambda e: db.Link(e.text), images.findall("image"))
    
    videos = org.find("videos")
    if videos is not None:
        org_model.videos = map(lambda e: db.Link(e.text), videos.findall("link"))
    
    social_networks = org.find("social_networks")
    if social_networks is not None:
        org_model.social_networks = map(lambda e: db.Link(e.text), social_networks.findall("link"))
    
    external_links = org.find("external_links")
    if external_links is not None:
      org_model.external_links = map(lambda e: db.Link(e.text), external_links.findall("link"))  
      debug(list(org_model.external_links))

    related_crises = org.find("related_crises")
    if related_crises is not None:
        org_model.related_crises = map(lambda e: e.text, related_crises.findall("crisisRef"))
    
    related_people = org.find("related_people")
    if related_orgs is not None:
        org_model.related_people = map(lambda e: e.text, related_people.findall("personRef"))

    imported.append(org_model)

  
  crises = root.find("crises").findall("crisis")
  for crisis in crises:
    crisis_model = Crisis(name = crisis.find("name").text)
    kind_ = crisis.find("kind")
    if kind_ is not None:
        crisis_model.kind_ = kind_.text
        debug(crisis_model.kind_)
        
    location = crisis.find("location")
    if location is not None:
        crisis_model.location = location.text

    date_and_time = crisis.find("date_and_time")
    if date_and_time is not None:
        crisis_model.date_and_time = date_and_time.text

    human_impact = crisis.find("human_impact")
    if human_impact is not None:
        crisis_model.human_impact = human_impact.text

    economic_impact = crisis.find("economic_impact")
    if economic_impact is not None:
        crisis_model.economic_impact = economic_impact.text

    resources_needed = crisis.find("resources_needed")
    if resources_needed is not None:
        crisis_model.resources_needed = resources_needed.text

    ways_to_help = crisis.find("ways_to_help")
    if ways_to_help is not None:
        crisis_model.ways_to_help = ways_to_help.text
        
    history = crisis.find("history")
    if history is not None:
        crisis_model.history = history.text
        
    images = crisis.find("images")
    if images is not None:
        crisis_model.images = map(lambda e: db.Link(e.text), images.findall("image"))
    
    videos = crisis.find("videos")
    if videos is not None:
        crisis_model.videos = map(lambda e: db.Link(e.text), videos.findall("link"))
    
    social_networks = crisis.find("social_networks")
    if social_networks is not None:
        crisis_model.social_networks = map(lambda e: db.Link(e.text), social_networks.findall("link"))
    
    external_links = crisis.find("external_links")
    if external_links is not None:
      crisis_model.external_links = map(lambda e: db.Link(e.text), external_links.findall("link"))  
      debug(list(crisis_model.external_links))

    related_people = crisis.find("related_people")
    if related_people is not None:
        crisis_model.related_people = map(lambda e: e.text, related_people.findall("personRef"))
    
    related_orgs = crisis.find("related_orgs")
    if related_orgs is not None:
        crisis_model.related_orgs = map(lambda e: e.text, related_orgs.findall("orgRef"))

    imported.append(crisis_model)
  
    
    
    
def debug(msg):
    logging.debug("\n\n" + str(msg) + "\n")

def main():
  application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)
