import sys

import wsgiref.handlers
import xml.etree.cElementTree as ET
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

import logging

data_models = {"people":{}, "crises":{}, "orgs":{}}

class Link(db.Model):
    site = db.StringProperty()
    title = db.StringProperty()
    url = db.LinkProperty()
    description = db.TextProperty()
    
class FullAddress(db.Model):
    address = db.StringProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    country = db.StringProperty()
    zip_ = db.StringProperty()
    
class ContactInfo(db.Model):
    phone = db.PhoneNumberProperty()
    email = db.EmailProperty()
    mail = FullAddress()
    
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
    
class Impact(db.Model):
    human = HumanImpact()
    economic = EconomicImpact()
    
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
    type_ = db.StringProperty()
    time = Date()
    loc = Location()
    impact = Impact()
    
class OrgInfo(db.Model):
    type_ = db.StringProperty()
    history = db.TextProperty()
    contact = ContactInfo()
    loc = Location()

class PersonInfo(db.Model):
    type_ = db.StringProperty()
    birthdate = Date()
    nationality = db.StringProperty()
    biography = db.TextProperty()
    
class Reference(db.Model):
    primaryImage = Link()
    images = []#db.ListProperty(Link)
    videos = []#db.ListProperty(Link)
    socials = []#db.ListProperty(Link)
    exts = []#db.ListProperty(Link)
    
class Crisis(db.Model):
    idref = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    info = CrisisInfo()
    ref = Reference()
    misc = db.StringProperty()
    relatedOrgs = []#db.ListProperty(db.ReferenceProperty(Organization))
    relatedPeople = []#db.ListProperty(db.ReferenceProperty(Person))

class Organization(db.Model):
    idref = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    info = OrgInfo()
    ref = Reference()
    misc = db.StringProperty()
    relatedCrises = []#db.ListProperty(db.ReferenceProperty(Crisis))
    relatedPeople = []#db.ListProperty(db.ReferenceProperty(Person))

class Person(db.Model):
    idref = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    info = PersonInfo()
    ref = Reference()
    misc = db.StringProperty()
    relatedCrises = []#db.ListProperty(db.ReferenceProperty(Crisis))
    relatedOrgs = []#db.ListProperty(db.ReferenceProperty(Organization))

class WorldCrises(db.Model):
    crises = []#db.ListProperty(Crisis)
    orgs = []#db.ListProperty(Organization)
    people = []#db.ListProperty(Person)
    
class MainHandler(webapp.RequestHandler):
    def get(self):
        """
        This method is called by the GAE when a user navigates to the root page.
        It draws the page.
        """
        path = self.request.path

        #crises = Crisis.all().fetch(50)
        #orgs = Organization.all().fetch(50)
        #people = Person.all().fetch(50)    
   
        crises = data_models['crises']
        orgs = data_models['orgs']
        people = data_models['people']    

        template_values = {
            'crises': crises,
            'people': people,
            'orgs': orgs,
        }

        self.response.headers['Content-Type'] = 'text/html'

        if path.startswith("/crises/") :
            self.response.out.write("crisis page yet to be implemented")
            self.response.out.write(crises.values())
        elif path.startswith("/orgs/") :
            self.response.out.write("org page yet to be implemented")
        elif path.startswith("/people/"):
            self.response.out.write("person page yet to be implemented")
        else:
            #self.response.out.write(template.render('djangogoodies/maintemplate.html', template_values))
            inFile = open("htmlgoodies/mockup.html", 'r')
            outstr = inFile.read() #"HELLO CAR RAMROD"
            inFile.close()
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
    
    data = {"people": {}, "crises": {}, "orgs": {}}
    
    crises = root.findall("crisis")
    for crisis in crises: 
        currentCrisis = Crisis(idref = crisis.attrib["id"], name = crisis.find("name").text)
        info = crisis.find("info")
        currentCrisis.info.history = info.find("history").text
        currentCrisis.info.help = info.find("help").text
        currentCrisis.info.resources = info.find("resources").text
        currentCrisis.info.type_ = info.find("type").text
        time = info.find("time")
        currentCrisis.info.time.time = time.find("time").text
        currentCrisis.info.time.day = int(time.find("day").text)
        currentCrisis.info.time.month = int(time.find("month").text)
        currentCrisis.info.time.year = int(time.find("year").text)
        currentCrisis.info.time.misc = time.find("misc").text
        loc = info.find("loc")
        currentCrisis.info.loc.city = loc.find("city").text
        currentCrisis.info.loc.region = loc.find("region").text
        currentCrisis.info.loc.country = loc.find("country").text
        impact = info.find("impact")
        human = impact.find("human")
        currentCrisis.info.impact.human.deaths = int(human.find("deaths").text)
        currentCrisis.info.impact.human.displaced = int(human.find("displaced").text)
        currentCrisis.info.impact.human.injured = int(human.find("injured").text)
        currentCrisis.info.impact.human.missing = int(human.find("missing").text)
        currentCrisis.info.impact.human.misc = human.find("misc").text
        economic = impact.find("economic")
        currentCrisis.info.impact.economic.amount = economic.find("amount").text
        currentCrisis.info.impact.economic.currency = economic.find("currency").text
        currentCrisis.info.impact.economic.misc = economic.find("misc").text
        ref = crisis.find("ref")
        primaryImage = ref.find("primaryImage")
        #currentCrisis.ref.append(Link(site = primaryImage.find("site").text, title = primaryImage.find("title").text, url = primaryImage.find("url").text, description = primaryImage.find("description").text))
        currentCrisis.ref.primaryImage = Link(site = primaryImage.find("site").text, title = primaryImage.find("title").text, url = primaryImage.find("url").text, description = primaryImage.find("description").text)
        images = ref.findall("image")
        for image in images:
            s = image.find("site")
            s = "" if s is None else s.text
            t = image.find("title")
            t = "" if t is None else t.text
            u = image.find("url").text
            d = image.find("description")
            d = "" if d is None else d.text
            currentCrisis.ref.images.append(Link(site = s, title = t, url = u, description = d))
            #currentCrisis.ref.images.append(Link(site = image.find("site").text, title = image.find("title").text, url = image.find("url").text, description = image.find("description").text))
        videos = ref.findall("video")
        for video in videos:
            s = video.find("site")
            s = "" if s is None else s.text
            t = video.find("title")
            t = "" if t is None else t.text
            u = video.find("url").text
            d = video.find("description")
            d = "" if d is None else d.text
            currentCrisis.ref.videos.append(Link(site = s, title = t, url = u, description = d))
            #currentCrisis.ref.videos.append(Link(site = video.find("site").text, title = video.find("title").text, url = video.find("url").text, description = video.find("description").text))
        socials = ref.findall("social") 
        for social in socials:
            s = social.find("site")
            s = "" if s is None else s.text
            t = social.find("title")
            t = "" if t is None else t.text
            u = social.find("url").text
            d = social.find("description")
            d = "" if d is None else d.text
            currentCrisis.ref.socials.append(Link(site = s, title = t, url = u, description = d))
            #currentCrisis.ref.socials.append(Link(site = social.find("site").text, title = social.find("title").text, url = social.find("url").text, description = social.find("description").text))
        exts = ref.findall("ext")
        for ext in exts:
            s = ext.find("site")
            s = "" if s is None else s.text
            t = ext.find("title")
            t = "" if t is None else t.text
            u = ext.find("url").text
            d = ext.find("description")
            d = "" if d is None else d.text
            currentCrisis.ref.exts.append(Link(site = s, title = t, url = u, description = d))
            #currentCrisis.ref.exts.append(Link(site = ext.find("site").text, title = ext.find("title").text, url = ext.find("url").text, description = ext.find("description").text))
        currentCrisis. misc = crisis.find("misc").text
        relatedOrgs = crisis.findall("org")
        for relatedOrg in relatedOrgs:
            currentCrisis.relatedOrgs.append(relatedOrg.attrib["idref"])
        relatedPeople = crisis.findall("person")
        for relatedPerson in relatedPeople:
            currentCrisis.relatedPeople.append(relatedPerson.attrib["idref"])
        data["crises"][currentCrisis.idref] = currentCrisis
    
    people = root.findall("person")
    for person in people: 
        currentPerson = Person(idref = person.attrib["id"], name = person.find("name").text)
        info = person.find("info")
        currentPerson.info.type_ = info.find("type").text
        birthdate = info.find("birthdate")
        currentPerson.info.birthdate.time = birthdate.find("time").text
        currentPerson.info.birthdate.day = int(birthdate.find("day").text)
        currentPerson.info.birthdate.month = int(birthdate.find("month").text)
        currentPerson.info.birthdate.year = int(birthdate.find("year").text)
        currentPerson.info.birthdate.misc = birthdate.find("misc").text
        currentPerson.info.nationality = info.find("nationality").text
        currentPerson.info.biography = info.find("biography").text
        ref = person.find("ref")
        primaryImage = ref.find("primaryImage")
        #currentPerson.ref.append(Link(site = primaryImage.find("site").text, title = primaryImage.find("title").text, url = primaryImage.find("url").text, description = primaryImage.find("description").text))
        currentPerson.ref.primaryImage = Link(site = primaryImage.find("site").text, title = primaryImage.find("title").text, url = primaryImage.find("url").text, description = primaryImage.find("description").text)
        images = ref.findall("image")
        for image in images:
            s = image.find("site")
            s = "" if s is None else s.text
            t = image.find("title")
            t = "" if t is None else t.text
            u = image.find("url").text
            d = image.find("description")
            d = "" if d is None else d.text
            currentPerson.ref.images.append(Link(site = s, title = t, url = u, description = d))
            #currentPerson.ref.images.append(Link(site = image.find("site").text, title = image.find("title").text, url = image.find("url").text, description = image.find("description").text))
        videos = ref.findall("video")
        for video in videos:
            s = video.find("site")
            s = "" if s is None else s.text
            t = video.find("title")
            t = "" if t is None else t.text
            u = video.find("url").text
            d = video.find("description")
            d = "" if d is None else d.text
            currentPerson.ref.videos.append(Link(site = s, title = t, url = u, description = d))
            #currentPerson.ref.videos.append(Link(site = video.find("site").text, title = video.find("title").text, url = video.find("url").text, description = video.find("description").text))
        debug(currentPerson.name)
        debug("FFFFFUUUUUUUU-")
        socials = ref.findall("social") 
        for social in socials:
            s = social.find("site")
            s = "" if s is None else s.text
            t = social.find("title")
            t = "" if t is None else t.text
            u = social.find("url").text
            d = social.find("description")
            d = "" if d is None else d.text
            currentPerson.ref.socials.append(Link(site = s, title = t, url = u, description = d))
            #currentPerson.ref.socials.append(Link(site = social.find("site").text, title = social.find("title").text, url = social.find("url").text, description = social.find("description").text))
        exts = ref.findall("ext")
        for ext in exts:
            s = ext.find("site")
            s = "" if s is None else s.text
            t = ext.find("title")
            t = "" if t is None else t.text
            u = ext.find("url").text
            d = ext.find("description")
            d = "" if d is None else d.text
            currentPerson.ref.exts.append(Link(site = s, title = t, url = u, description = d))
            #currentPerson.ref.exts.append(Link(site = ext.find("site").text, title = ext.find("title").text, url = ext.find("url").text, description = ext.find("description").text))
        misc = person.find("misc").text
        relatedCrises = person.findall("crisis")
        for relatedCrisis in relatedCrises:
            currentPerson.relatedCrises.append(relatedCrisis.attrib["idref"])
        relatedOrgs = person.findall("org")
        for relatedOrg in relatedOrgs:
            currentPerson.relatedOrgs.append(relatedOrg.attrib["idref"])
        data["people"][currentPerson.idref] = currentPerson
        
    orgs = root.findall("org")
    for org in orgs: 
        currentOrg = Organization(idref = org.attrib["id"], name = org.find("name").text)
        info = org.find("info")
        currentOrg.info.type_ = info.find("type").text
        currentOrg.info.history = info.find("history").text
        contact = info.find("contact")
        currentOrg.info.phone = contact.find("phone").text
        currentOrg.info.email = contact.find("email").text
        mail = contact.find("mail")
        currentOrg.info.addr = mail.find("address").text
        currentOrg.info.city = mail.find("city").text
        currentOrg.info.state = mail.find("state").text
        currentOrg.info.country = mail.find("country").text
        currentOrg.info.zip = mail.find("zip").text
        loc = info.find("loc")
        currentCrisis.info.loc.city = loc.find("city").text
        currentCrisis.info.loc.region = loc.find("region").text
        currentCrisis.info.loc.country = loc.find("country").text
        ref = org.find("ref")
        primaryImage = ref.find("primaryImage")
        #currentOrg.ref.append(Link(site = primaryImage.find("site").text, title = primaryImage.find("title").text, url = primaryImage.find("url").text, description = primaryImage.find("description").text))
        currentOrg.ref.primaryImage = Link(site = primaryImage.find("site").text, title = primaryImage.find("title").text, url = primaryImage.find("url").text, description = primaryImage.find("description").text)
        images = ref.findall("image")
        for image in images:
            s = image.find("site")
            s = "" if s is None else s.text
            t = image.find("title")
            t = "" if t is None else t.text
            u = image.find("url").text
            d = image.find("description")
            d = "" if d is None else d.text
            currentOrg.ref.images.append(Link(site = s, title = t, url = u, description = d))
            #currentOrg.ref.images.append(Link(site = image.find("site").text, title = image.find("title").text, url = image.find("url").text, description = image.find("description").text))
        videos = ref.findall("video")
        for video in videos:
            s = video.find("site")
            s = "" if s is None else s.text
            t = video.find("title")
            t = "" if t is None else t.text
            u = video.find("url").text
            d = video.find("description")
            d = "" if d is None else d.text
            currentOrg.ref.videos.append(Link(site = s, title = t, url = u, description = d))
            #currentOrg.ref.videos.append(Link(site = video.find("site").text, title = video.find("title").text, url = video.find("url").text, description = video.find("description").text))
        socials = ref.findall("social") 
        for social in socials:
            s = social.find("site")
            s = "" if s is None else s.text
            t = social.find("title")
            t = "" if t is None else t.text
            u = social.find("url").text
            d = social.find("description")
            d = "" if d is None else d.text
            currentOrg.ref.socials.append(Link(site = s, title = t, url = u, description = d))
            #currentOrg.ref.socials.append(Link(site = social.find("site").text, title = social.find("title").text, url = social.find("url").text, description = social.find("description").text))
        exts = ref.findall("ext")
        for ext in exts:
            s = ext.find("site")
            s = "" if s is None else s.text
            t = ext.find("title")
            t = "" if t is None else t.text
            u = ext.find("url").text
            d = ext.find("description")
            d = "" if d is None else d.text
            currentOrg.ref.exts.append(Link(site = s, title = t, url = u, description = d))
            #currentOrg.ref.exts.append(Link(site = ext.find("site").text, title = ext.find("title").text, url = ext.find("url").text, description = ext.find("description").text))
        currentOrg.misc = org.find("misc").text
        relatedCrises = org.findall("crisis")
        for relatedCrisis in relatedCrises:
            currentOrg.relatedCrises.append(relatedCrisis.attrib["idref"])
        relatedPeople = org.findall("person")
        for relatedPerson in relatedPeople:
            currentOrg.relatedPeople.append(relatedPerson.attrib["idref"])
        data["crises"][currentOrg.idref] = currentOrg
        
    return data

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

# ---------
# ExportXml
# ---------

def ExportXml(data):
    """
    Exports the data to the screen in xml format
    data is the data
    return a string in xml format
    """
    
    myString = ["<worldCrises>\n"]
    
    for crisis in data["crises"]:
        myString.append("\t<crisis>\n")
        myString.append("\t\t<name>" + data["crises"][crisis].name + "</name>\n")
        myString.append("\t\t<info>\n")
        myString.append("\t\t\t<history>" + data["crises"][crisis].info.history + "</history>\n")
        myString.append("\t\t\t<help>" + data["crises"][crisis].info.help + "</help>\n")
        myString.append("\t\t\t<resources>" + data["crises"][crisis].info.resources + "</resources>\n")
        myString.append("\t\t\t<type>" + data["crises"][crisis].info.type_ + "</type>\n")
        myString.append("\t\t\t<history>" + data["crises"][crisis].info.history + "</history>\n")
        myString.append("\t\t\t<time>\n")
        myString.append("\t\t\t\t<time>" + data["crises"][crisis].info.time.time + "</time>\n")
        myString.append("\t\t\t\t<day>" + data["crises"][crisis].info.time.day + "</day>\n")
        myString.append("\t\t\t\t<month>" + data["crises"][crisis].info.time.month + "</month>\n")
        myString.append("\t\t\t\t<year>" + data["crises"][crisis].info.time.year + "</year>\n")
        myString.append("\t\t\t\t<misc>" + data["crises"][crisis].info.time.misc + "</misc>\n")
        myString.append("\t\t\t</time>\n")
        myString.append("\t\t\t<loc>\n")
        myString.append("\t\t\t\t<city>" + data["crises"][crisis].info.loc.city + "</city>\n")
        myString.append("\t\t\t\t<region>" + data["crises"][crisis].info.loc.region + "</region>\n")
        myString.append("\t\t\t\t<country>" + data["crises"][crisis].info.loc.country + "</country>\n")
        myString.append("\t\t\t</loc>\n")
        myString.append("\t\t\t<impact>\n")
        myString.append("\t\t\t\t<human>\n")
        myString.append("\t\t\t\t\t<deaths>" + data["crises"][crisis].info.impact.human.deaths + "</deaths>\n")
        myString.append("\t\t\t\t\t<displaced>" + data["crises"][crisis].info.impact.human.displaced + "</displaced>\n")
        myString.append("\t\t\t\t\t<injured>" + data["crises"][crisis].info.impact.human.injured + "</injured>\n")
        myString.append("\t\t\t\t\t<missing>" + data["crises"][crisis].info.impact.human.missing + "</missing>\n")
        myString.append("\t\t\t\t\t<misc>" + data["crises"][crisis].info.impact.human.misc + "</misc>\n")
        myString.append("\t\t\t\t</human>\n")
        myString.append("\t\t\t\t<economic>\n")
        myString.append("\t\t\t\t\t<amount>" + data["crises"][crisis].info.impact.economic.amount + "</amount>\n")
        myString.append("\t\t\t\t\t<currency>" + data["crises"][crisis].info.impact.economic.currency + "</currency>\n")
        myString.append("\t\t\t\t\t<misc>" + data["crises"][crisis].info.impact.economic.misc + "</misc>\n")
        myString.append("\t\t\t\t</economic>\n")
        myString.append("\t\t\t</impact>\n")
        myString.append("\t\t</info>\n")
        myString.append("\t\t<ref>\n")
        myString.append("\t\t\t<primaryImage>\n")
        myString.append("\t\t\t\t<site>" + data["crises"][crisis].ref.primaryImage.site + "</site>\n")
        myString.append("\t\t\t\t<title>" + data["crises"][crisis].ref.primaryImage.title + "</title>\n")
        myString.append("\t\t\t\t<url>" + data["crises"][crisis].ref.primaryImage.url + "</url>\n")
        myString.append("\t\t\t\t<description>" + data["crises"][crisis].ref.primaryImage.description + "</description>\n")
        myString.append("\t\t\t</primaryImage>\n")
        for image in data["crises"][crisis].ref.images:
        	myString.append("\t\t\t<image>\n")
        	myString.append("\t\t\t\t<site>" + data["crises"][crisis].ref.image.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["crises"][crisis].ref.image.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["crises"][crisis].ref.image.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["crises"][crisis].ref.image.description + "</description>\n")
        	myString.append("\t\t\t</image>\n")
        for video in data["crises"][crisis].ref.videos:
        	myString.append("\t\t\t<video>\n")
        	myString.append("\t\t\t\t<site>" + data["crises"][crisis].ref.video.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["crises"][crisis].ref.video.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["crises"][crisis].ref.video.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["crises"][crisis].ref.video.description + "</description>\n")
        	myString.append("\t\t\t</video>\n")
        for social in data["crises"][crisis].ref.socials:
        	myString.append("\t\t\t<social>\n")
        	myString.append("\t\t\t\t<site>" + data["crises"][crisis].ref.social.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["crises"][crisis].ref.social.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["crises"][crisis].ref.social.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["crises"][crisis].ref.social.description + "</description>\n")
        	myString.append("\t\t\t</social>\n")
        for ext in data["crises"][crisis].ref.exts:
        	myString.append("\t\t\t<ext>\n")
        	myString.append("\t\t\t\t<site>" + data["crises"][crisis].ref.ext.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["crises"][crisis].ref.ext.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["crises"][crisis].ref.ext.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["crises"][crisis].ref.ext.description + "</description>\n")
        	myString.append("\t\t\t</ext>\n")
        myString.append("\t\t</ref>\n")
        myString.append("\t\t<misc>" + data["crises"][crisis].misc + "</misc>\n")
        
        """
        for orgs in data["crises"][crisis].org:
        	myString.append("\t\t<org " #...
        	#..
        for person in data["crises"][crisis]:
        	myString.append(...)
        """
        myString += "\t<\crisis>\n"
        
    for org in data["orgs"]:
        #myString.append("\t<organization>" + data["orgs"][org].id + ">\n")
        myString.append("\t\t<name>" + data["orgs"][org].name + "</name>\n")
        myString.append("\t\t<info>\n")
        myString.append("\t\t\t<type>" + data["orgs"][org].info.type_ + "</type>\n")
        myString.append("\t\t\t<history>" + data["orgs"][org].info.history + "</history>\n")
        myString.append("\t\t\t<contact>\n")
        myString.append("\t\t\t\t<phone>" + data["orgs"][org].info.contact.phone + "</phone>\n")
        myString.append("\t\t\t\t<email>" + data["orgs"][org].info.contact.email + "</email>\n")
        myString.append("\t\t\t\t<mail>\n")
        myString.append("\t\t\t\t\t<address>" + data["orgs"][org].info.contact.mail.address + "</address>\n")
        myString.append("\t\t\t\t\t<city>" + data["orgs"][org].info.contact.mail.city + "</city>\n")
        myString.append("\t\t\t\t\t<state>" + data["orgs"][org].info.contact.mail.state + "</state>\n")
        myString.append("\t\t\t\t\t<country>" + data["orgs"][org].info.contact.mail.country + "</country>\n")
        myString.append("\t\t\t\t\t<zip>" + data["orgs"][org].info.contact.mail.zip + "</zip>\n")
        myString.append("\t\t\t\t</mail>\n")
        myString.append("\t\t\t</contact>\n")
        myString.append("\t\t\t<loc>\n")
        myString.append("\t\t\t\t<city>" + data["orgs"][org].info.loc.city + "</city>\n")
        myString.append("\t\t\t\t<region>" + data["orgs"][org].info.loc.region + "</region>\n")
        myString.append("\t\t\t\t<country>" + data["orgs"][org].info.loc.country + "</country>\n")
        myString.append("\t\t\t</loc>\n")
        myString.append("\t\t</info>\n")
        myString.append("\t\t<ref>\n")
        myString.append("\t\t\t<primaryImage>\n")
        myString.append("\t\t\t\t<site>" + data["orgs"][org].ref.primaryImage.site + "</site>\n")
        myString.append("\t\t\t\t<title>" + data["orgs"][org].ref.primaryImage.title + "</title>\n")
        myString.append("\t\t\t\t<url>" + data["orgs"][org].ref.primaryImage.url + "</url>\n")
        myString.append("\t\t\t\t<description>" + data["orgs"][org].ref.primaryImage.description + "</description>\n")
        myString.append("\t\t\t</primaryImage>\n")
        for image in data["orgs"][org].ref.images:
        	myString.append("\t\t\t<image>\n")
        	myString.append("\t\t\t\t<site>" + data["orgs"][org].ref.image.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["orgs"][org].ref.image.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["orgs"][org].ref.image.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["orgs"][org].ref.image.description + "</description>\n")
        	myString.append("\t\t\t</image>\n")
        for video in data["orgs"][org].ref.videos:
        	myString.append("\t\t\t<video>\n")
        	myString.append("\t\t\t\t<site>" + data["orgs"][org].ref.video.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["orgs"][org].ref.video.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["orgs"][org].ref.video.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["orgs"][org].ref.video.description + "</description>\n")
        	myString.append("\t\t\t</video>\n")
        for social in data["orgs"][org].ref.socials:
        	myString.append("\t\t\t<social>\n")
        	myString.append("\t\t\t\t<site>" + data["orgs"][org].ref.social.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["orgs"][org].ref.social.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["orgs"][org].ref.social.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["orgs"][org].ref.social.description + "</description>\n")
        	myString.append("\t\t\t</social>\n")
        for ext in data["orgs"][org].ref.exts:
        	myString.append("\t\t\t<ext>\n")
        	myString.append("\t\t\t\t<site>" + data["orgs"][org].ref.ext.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["orgs"][org].ref.ext.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["orgs"][org].ref.ext.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["orgs"][org].ref.ext.description + "</description>\n")
        	myString.append("\t\t\t</ext>\n")
        myString.append("\t\t</ref>\n")
        myString.append("\t\t<misc>" + data["orgs"][org].misc + "</misc>\n")
        #some stuff about the idrefs of related crisis and person
        myString += "\t<\organization>\n"
        
    for person in data["people"]:
        #myString.append("\t<person>" + data["people"][person].id + ">\n")
        myString.append("\t\t<name>" + data["people"][person].name + "</name>\n")
        myString.append("\t\t<info>\n")
        myString.append("\t\t\t<type>" + data["people"][person].info.type_ + "</type>\n")
        myString.append("\t\t\t<birthdate>\n")
        myString.append("\t\t\t\t<time>" + data["people"][person].info.birthdate.time + "</time>\n")
        myString.append("\t\t\t\t<day>" + data["people"][person].info.birthdate.day + "</day>\n")
        myString.append("\t\t\t\t<year>" + data["people"][person].info.birthdate.year + "</year>\n")
        myString.append("\t\t\t\t<misc>" + data["people"][person].info.birthdate.misc + "</misc>\n")
        myString.append("\t\t\t</birthdate>\n")
        myString.append("\t\t\t<nationality>" + data["people"][person].info.nationality + "</nationality>\n")
        myString.append("\t\t\t<biography>" + data["people"][person].info.biography + "</biography>\n")
        myString.append("\t\t</info>\n")
        myString.append("\t\t<ref>\n")
        myString.append("\t\t\t<primaryImage>\n")
        myString.append("\t\t\t\t<site>" + data["people"][person].ref.primaryImage.site + "</site>\n")
        myString.append("\t\t\t\t<title>" + data["people"][person].ref.primaryImage.title + "</title>\n")
        myString.append("\t\t\t\t<url>" + data["people"][person].ref.primaryImage.url + "</url>\n")
        myString.append("\t\t\t\t<description>" + data["people"][person].ref.primaryImage.description + "</description>\n")
        myString.append("\t\t\t</primaryImage>\n")
        for image in data["people"][org].ref.images:
        	myString.append("\t\t\t<image>\n")
        	myString.append("\t\t\t\t<site>" + data["people"][person].ref.image.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["people"][person].ref.image.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["people"][person].ref.image.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["people"][person].ref.image.description + "</description>\n")
        	myString.append("\t\t\t</image>\n")
        for video in data["people"][person].ref.videos:
        	myString.append("\t\t\t<video>\n")
        	myString.append("\t\t\t\t<site>" + data["people"][person].ref.video.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["people"][person].ref.video.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["people"][person].ref.video.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["people"][person].ref.video.description + "</description>\n")
        	myString.append("\t\t\t</video>\n")
        for social in data["people"][person].ref.socials:
        	myString.append("\t\t\t<social>\n")
        	myString.append("\t\t\t\t<site>" + data["people"][person].ref.social.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["people"][person].ref.social.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["people"][person].ref.social.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["people"][person].ref.social.description + "</description>\n")
        	myString.append("\t\t\t</social>\n")
        for ext in data["people"][person].ref.exts:
        	myString.append("\t\t\t<ext>\n")
        	myString.append("\t\t\t\t<site>" + data["people"][person].ref.ext.site + "</site>\n")
        	myString.append("\t\t\t\t<title>" + data["people"][person].ref.ext.title + "</title>\n")
        	myString.append("\t\t\t\t<url>" + data["people"][person].ref.ext.url + "</url>\n")
        	myString.append("\t\t\t\t<description>" + data["people"][person].ref.ext.description + "</description>\n")
        	myString.append("\t\t\t</ext>\n")
        myString.append("\t\t</ref>\n")
        myString.append("\t\t<misc>" + data["people"][person].misc + "</misc>\n")
        #some stuff about the idrefs of related crisis and person
        myString.append("\t<\person>\n")
    
    myString.append("</worldCrises>")
    test = "".join(myString)
    return test

# -----
# Debug
# -----

def debug(msg):
    """
    prints the debug message
    msg the string you want to put on the debug screen
    """
    logging.debug("\n\n" + str(msg) + "\n")

def main():
    application = webapp.WSGIApplication([  ('/', MainHandler), 
                                            ('/import', ImportFormHandler), 
                                            ('/import_upload', ImportUploadHandler),
                                            ('/export', ExportHandler),
                                            ('/.*', MainHandler)
                                         ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

