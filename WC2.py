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
    ref = db.ListProperty(Link)
    misc = db.StringProperty()
    related_orgs = db.ListProperty(Reference)
    related_people = db.ListProperty(Reference)

class Organization(db.Model):
    name = db.StringProperty(required=True)
    info = OrgInfo()
    ref = db.ListProperty(Link)
    misc = db.StringProperty()
    related_crises = db.ListProperty(Reference)
    related_people = db.ListProperty(Reference)

class Person(db.Model):
    name = db.StringProperty(required=True)
    info = PersonInfo()
    ref = db.ListProperty(Link)
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

class Reference(db.Model):
    primaryImage = Link()
    images = db.ListProperty(Link)
    videos = db.ListProperty(Link)
    social = db.ListProperty(Link)
    ext = db.ListProperty(Link)

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
    
class MainHandler(webapp.RequestHandler):
    def get(self):
        """
        This method is called by the GAE when a user navigates to the root page.
        It draws the page.
        """
        self.response.headers['Content-Type'] = 'text/html'

        inFile = open("htmlgoodies/mockup.html", 'r')
        outstr = inFile.read() #"HELLO CAR RAMROD"
        inFile.close()
        imported = ImportXml("WC1.xml")
        debug("IMPORTED: " + str(imported))
        self.response.out.write(outstr)

class ExportHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(ExportXml(data_models))

class ImportFormHandler(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/import_upload')
        self.response.out.write('<html><body><table align="center" width="100%" height="100%"><tr height="200"><td></td></tr>')
        self.response.out.write('<tr><td><form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write('''Upload File: <input type="file" name="file"><br> <input type="submit"
            name="submit" value="Submit"> </form></td></tr><tr height="200"><td></td></tr></table></body></html>''')


class ImportUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            global data_models
            xml_file = self.get_uploads('file')[0].open()
            debug("XML_FILE: "+ str(xml_file))
            data_models = import_file(xml_file)
            debug("DATA_MODELS: " + str(data_models))
            self.response.out.write("Data was successfully imported")
        except:
            self.response.out.write("Please provide a valid XML file")
            
# ---------
# ImportXml
# ---------
def ImportXml(filename):
    """
    Imports data from an xml instance and saves it in heap
    Assumes valid xml instance
    filename the name of the .xml file
    return the desired data in multi-dimensional dictionary
    """
    return import_file(open(filename, "r"))

# -----------
# import_file
# -----------
def import_file(xml_file):
    tree = ET.ElementTree(file = xml_file)
    root = tree.getroot()
    
    imported = {"people": {}, "crises": {}, "orgs": {}}
    
    crises = root.findall("crisis")
    for crisis in crises: 
        current_crisis = Crisis(name = crisis.find("name").text)
        info = crisis.find("info")
        current_crisis.info.history = info.find("history").text
        current_crisis.info.help = info.find("help").text
        current_crisis.info.resources = info.find("resources").text
        current_crisis.info._type = info.find("type").text
        time = info.find("time")
        current_crisis.info.time = time.find("time").text
        current_crisis.info.day = time.find("day").text
        current_crisis.info.month = time.find("month").text
        current_crisis.info.year = time.find("year").text
        current_crisis.info.misc = time.find("misc").text
        loc = crisis.find("loc")
        current_crisis.info.loc.city = loc.find("city").text
        current_crisis.info.loc.region = loc.find("region").text
        current_crisis.info.loc.country = loc.find("country").text
        impact = crisis.find("impact")
        human = impact.find("human")
        current_crisis.info.impact.human.deaths = human.find("deaths").text
        current_crisis.info.impact.human.displaced = human.find("displaced").text
        current_crisis.info.impact.human.injured = human.find("injured").text
        current_crisis.info.impact.human.missing = human.find("missing").text
        current_crisis.info.impact.human.misc = human.find("misc").text
        economic = impact.find("economic")
        current_crisis.info.impact.economic.amount = economic.find("amount").text
        current_crisis.info.impact.economic.currency = economic.find("currency").text
        current_crisis.info.impact.economic.misc = economic.find("misc").text
        ref = crisis.find("ref")
        primaryImage = ref.find("primaryImage")
        current_crisis.ref.append(Link(site = primaryImage.find("site"), title = primaryImage.find("title"), url = primaryImage.find("url"), description = primaryImage.find("description")))
        images = ref.findall("image")
        for image in images:
            current_crisis.ref.append(Link(site = image.find("site"), title = image.find("title"), url = image.find("url"), description = image.find("description")))
        videos = ref.findall("video")
        for video in videos:
            current_crisis.ref.append(Link(site = video.find("site"), title = video.find("title"), url = video.find("url"), description = video.find("description")))
        current_crisis.ref.links.
        

    people = root.findall("person")
    for person in people: 
        current_person = Person(name = person.find("name").text)
        info = person.find("info")
        current_person.info._type = info.find("type").text
        current_person.info.nationality = info.find("nationality").text
        current_person.info.biography = info.find("biography").text
        birthdate = info.find("birthdate").text
        current_person.info.time = birthdate.find("time").text
        current_person.info.day = birthdate.find("day").text
        current_person.info.month = birthdate.find("month").text
        current_person.info.year = bithdate.find("year").text
        current_person.info.misc = bithdate.find("misc").text
        ref = person.find("ref")
        primaryImage = ref.find("primaryImage")
        current_person.ref.append(Link(site = primaryImage.find("site"), title = primaryImage.find("title"), url = primaryImage.find("url"), description = primaryImage.find("description")))
        images = ref.findall("image")
        for image in images:
            current_person.ref.append(Link(site = image.find("site"), title = image.find("title"), url = image.find("url"), description = image.find("description")))
        videos = ref.findall("video")
        for video in videos:
            current_person.ref.append(Link(site = video.find("site"), title = video.find("title"), url = video.find("url"), description = video.find("description")))
        social = ref.find("social") 
        current_person.ref.append(Link(site = social.find("site"), title = primaryImage.find("title"), url = primaryImage.find("url"), description = primaryImage.find("description")))
        exts = ref.findall("ext")
        for ext in exts:
        	current_person.ref.append(Link(site = ext.find("site"), title = image.find("title"), url = image.find("url"), description = image.find("description")))
        misc = person.find("misc")
        
    
    return imported

# ------
# fixAmp
# ------
def fixAmp(line):
    """
    Replaces every occurrence of an ampersand(&) with "&amp;" in a given string
    line the original string
    return the modified string
    """
    result = ""
    for c in line:
        if c == '&':
            result += "&amp;"
        else:
            result += c
    return result


