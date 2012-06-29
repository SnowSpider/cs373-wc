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
    
    



