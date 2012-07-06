import sys

import wsgiref.handlers
import xml.etree.cElementTree as ET
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import logging

data_models = {"people":[], "crises":[], "orgs":[]}

class WorldCrises(db.Model):
    crises = db.ListProperty(Crisis);
    orgs = db.ListProperty(Organization);
    people = db.ListProperty(Person);
    
class Crisis(db.Model):
    name = db.StringProperty(required=True)
    info = PersonInfo()
    links = db.ListProperty(Link)
    misc = db.StringProperty()
    related_orgs = db.ListProperty(Reference)
    related_people = db.ListProperty(Reference)

class Organization(db.Model):
    name = db.StringProperty(required=True)
    info = OrgInfo()
    links = db.ListProperty(Link)
    misc = db.StringProperty()
    related_crises = db.ListProperty(Reference)
    related_people = db.ListProperty(Reference)

class Person(db.Model):
    name = db.StringProperty(required=True)
    info = PersonInfo()
    links = db.ListProperty(Link)
    misc = db.StringProperty()
    related_crises = db.ListProperty(Reference)
    related_orgs = db.ListProperty(Reference)
    
class Location(db.Model):
    city = db.StringProperty()
    region = db.StringProperty()
    country = db.StringProperty()
    
class Date(db.Model):
    time = db.StringProperty()
    day = db.IntegerProperty()
    month = db.IntegerProperty()
    year = db.IntegerProperty()
    misc = db.StringProperty()

class CrisisInfo(db.Model):
    history = db.TextProperty()
    help = db.StringProperty()
    resources = db.StringProperty()
    _type = db.StringProperty()
    time = Date()
    loc = Location()
    impact = Impact()
    
class OrgInfo(db.Model):
    _type = db.StringProperty()
    history = db.TextProperty()
    contact = ContactInfo()
    loc = Location()

class PersonInfo(db.Model):
    _type = db.StringProperty()
    birthDate = Date()
    nationality = db.StringProperty()
    biography = db.TextProperty()

class ContactInfo(db.Model):
    phone = db.PhoneNumberProperty()
    email = db.EmailProperty()
    mail = FullAddress()

class Impact(db.Model):
    human = HumanImpact()
    economic = EconomicImpact()

class HumanImpact(db.Model):
    deaths = db.IntegerProperty()
    displaced = db.IntegerProperty()
    injured = db.IntegerProperty()
    missing = db.IntegerProperty()
    misc = db.StringProperty()

class EconomicImpact(db.Model):
    amount = db.StringProperty()
    currency = db.IntegerProperty()
    misc = db.StringProperty()

class Link(db.Model):
    site = db.StringProperty()
    title = db.StringProperty()
    url = db.LinkProperty()
    description = db.TextProperty()

class Reference():
    # ???

class FullAddress():
    address = db.StringProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    country = db.StringProperty()
    _zip = db.StringProperty()
    



