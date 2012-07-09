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
    _zip = db.StringProperty()
    
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
    
class Reference(db.Model):
    primaryImage = Link()
    images = db.ListProperty(Link)
    videos = db.ListProperty(Link)
    socials = db.ListProperty(Link)
    exts = db.ListProperty(Link)
    
class Crisis(db.Model):
    name = db.StringProperty(required=True)
    info = PersonInfo()
    ref = Reference()
    misc = db.StringProperty()
    relatedOrgs = db.ListProperty(db.ReferenceProperty(Organization))
    relatedPeople = db.ListProperty(db.ReferenceProperty(Person))

class WorldCrises(db.Model):
    crises = db.ListProperty(Crisis);
    orgs = db.ListProperty(Organization);
    people = db.ListProperty(Person);

class Organization(db.Model):
    name = db.StringProperty(required=True)
    info = OrgInfo()
    ref = Reference()
    misc = db.StringProperty()
    relatedCrises = db.ListProperty(db.ReferenceProperty(Crisis))
    relatedPeople = db.ListProperty(db.ReferenceProperty(Person))

class Person(db.Model):
    name = db.StringProperty(required=True)
    info = PersonInfo()
    ref = Reference()
    misc = db.StringProperty()
    relatedCrises = db.ListProperty(db.ReferenceProperty(Crisis))
    relatedOrgs = db.ListProperty(db.ReferenceProperty(Organization))
    
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
        currentCrisis = Crisis(name = crisis.find("name").text)
        info = crisis.find("info")
        currentCrisis.info.history = info.find("history").text
        currentCrisis.info.help = info.find("help").text
        currentCrisis.info.resources = info.find("resources").text
        currentCrisis.info._type = info.find("type").text
        time = info.find("time")
        currentCrisis.info.time = time.find("time").text
        currentCrisis.info.day = time.find("day").text
        currentCrisis.info.month = time.find("month").text
        currentCrisis.info.year = time.find("year").text
        currentCrisis.info.misc = time.find("misc").text
        loc = info.find("loc")
        currentCrisis.info.loc.city = loc.find("city").text
        currentCrisis.info.loc.region = loc.find("region").text
        currentCrisis.info.loc.country = loc.find("country").text
        impact = info.find("impact")
        human = impact.find("human")
        currentCrisis.info.impact.human.deaths = human.find("deaths").text
        currentCrisis.info.impact.human.displaced = human.find("displaced").text
        currentCrisis.info.impact.human.injured = human.find("injured").text
        currentCrisis.info.impact.human.missing = human.find("missing").text
        currentCrisis.info.impact.human.misc = human.find("misc").text
        economic = impact.find("economic")
        currentCrisis.info.impact.economic.amount = economic.find("amount").text
        currentCrisis.info.impact.economic.currency = economic.find("currency").text
        currentCrisis.info.impact.economic.misc = economic.find("misc").text
        ref = crisis.find("ref")
        primaryImage = ref.find("primaryImage")
        currentCrisis.ref.append(Link(site = primaryImage.find("site"), title = primaryImage.find("title"), url = primaryImage.find("url"), description = primaryImage.find("description")))
        images = ref.findall("image")
        for image in images:
            currentCrisis.ref.append(Link(site = image.find("site"), title = image.find("title"), url = image.find("url"), description = image.find("description")))
        videos = ref.findall("video")
        for video in videos:
            currentCrisis.ref.append(Link(site = video.find("site"), title = video.find("title"), url = video.find("url"), description = video.find("description")))
        socials = ref.findall("social") 
        for social in socials:
        	currentCrisis.ref.append(Link(site = social.find("site"), title = social.find("title"), url = social.find("url"), description = social.find("description")))
        exts = ref.findall("ext")
        for ext in exts:
        	currentCrisis.ref.append(Link(site = ext.find("site"), title = ext.find("title"), url = ext.find("url"), description = ext.find("description")))
        currentCrisis. misc = crisis.find("misc").text
        relatedOrgs = crisis.findall("org")
        for relatedOrg in relatedOrgs:
            currentCrisis.relatedOrgs.append(relatedOrg)
        relatedPeople = crisis.findall("person")
        for relatedPerson in relatedPeople:
            currentCrisis.relatedPeople.append(relatedPerson)
        data["crises"][currentCrisis.name] = currentCrisis;
    
    people = root.findall("person")
    for person in people: 
        currentPerson = Person(name = person.find("name").text)
        info = person.find("info")
        currentPerson.info._type = info.find("type").text
        birthdate = info.find("birthdate").text
        currentPerson.info.time = birthdate.find("time").text
        currentPerson.info.day = birthdate.find("day").text
        currentPerson.info.month = birthdate.find("month").text
        currentPerson.info.year = bithdate.find("year").text
        currentPerson.info.misc = bithdate.find("misc").text
        currentPerson.info.nationality = info.find("nationality").text
        currentPerson.info.biography = info.find("biography").text
        ref = person.find("ref")
        primaryImage = ref.find("primaryImage")
        currentPerson.ref.append(Link(site = primaryImage.find("site"), title = primaryImage.find("title"), url = primaryImage.find("url"), description = primaryImage.find("description")))
        images = ref.findall("image")
        for image in images:
            currentPerson.ref.append(Link(site = image.find("site"), title = image.find("title"), url = image.find("url"), description = image.find("description")))
        videos = ref.findall("video")
        for video in videos:
            currentPerson.ref.append(Link(site = video.find("site"), title = video.find("title"), url = video.find("url"), description = video.find("description")))
        socials = ref.find("social") 
        for social in socials:
        	currentPerson.ref.append(Link(site = social.find("site"), title = social.find("title"), url = social.find("url"), description = social.find("description")))
        exts = ref.findall("ext")
        for ext in exts:
        	currentPerson.ref.append(Link(site = ext.find("site"), title = ext.find("title"), url = ext.find("url"), description = ext.find("description")))
        misc = person.find("misc").text
        relatedCrises = person.findall("crisis")
        for relatedCrisis in relatedCrises:
            currentPerson.relatedCrises.append(relatedCrisis)
        relatedOrgs = person.findall("org")
        for relatedOrg in relatedOrgs:
            currentPerson.relatedOrgs.append(relatedOrg)
        data["people"][currentPerson.name] = currentPerson
        
    orgs = root.findall("org")
    for org in orgs: 
        currentOrg = Organization(name = org.find("name").text)
        info = org.find("info")
        currentOrg.info._type = info.find("type").text
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
        #currentOrg.ref.primaryImage = something
        #currentOrg.ref.images.append(...)
        currentOrg.ref.append(Link(site = primaryImage.find("site"), title = primaryImage.find("title"), url = primaryImage.find("url"), description = primaryImage.find("description")))
        images = ref.findall("image")
        for image in images:
            currentOrg.ref.append(Link(site = image.find("site"), title = image.find("title"), url = image.find("url"), description = image.find("description")))
        videos = ref.findall("video")
        for video in videos:
            currentOrg.ref.append(Link(site = video.find("site"), title = video.find("title"), url = video.find("url"), description = video.find("description")))
        socials = ref.find("social") 
        for social in socials:
        	currentOrg.ref.append(Link(site = social.find("site"), title = social.find("title"), url = social.find("url"), description = social.find("description")))
        exts = ref.findall("ext")
        for ext in exts:
        	currentOrg.ref.append(Link(site = ext.find("site"), title = ext.find("title"), url = ext.find("url"), description = ext.find("description")))
        currentOrg.misc = org.find("misc").text
        relatedCrises = org.findall("crisis")
        for relatedCrisis in relatedCrises:
            currentOrg.relatedCrises.append(relatedCrisis)
        relatedPeople = org.findall("person")
        for relatedPerson in relatedPeople:
            currentOrg.relatedPeople.append(relatedPerson)
        data["crises"][currentOrg.name] = currentOrg;
        
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
        mystring.append("\t\t\t<history>" + data["crises"][crisis].info.history + "</history>\n")
        mystring.append("\t\t\t<help>" + data["crises"][crisis].info.help + "</help>\n")
        mystring.append("\t\t\t<resources>" + data["crises"][crisis].info.resources + "</resources>\n")
        mystring.append("\t\t\t<type>" + data["crises"][crisis].info.type + "</type>\n")
        mystring.append("\t\t\t<history>" + data["crises"][crisis].info.history + "</history>\n")
        myString.append("\t\t\t<time>\n")
        mystring.append("\t\t\t\t<time>" + data["crises"][crisis].info.time.time + "</time>\n")
        mystring.append("\t\t\t\t<day>" + data["crises"][crisis].info.time.day + "</day>\n")
        mystring.append("\t\t\t\t<month>" + data["crises"][crisis].info.time.month + "</month>\n")
        mystring.append("\t\t\t\t<year>" + data["crises"][crisis].info.time.year + "</year>\n")
        mystring.append("\t\t\t\t<misc>" + data["crises"][crisis].info.time.misc + "</misc>\n")
        myString.append("\t\t\t</time>\n")
        myString.append("\t\t\t<loc>\n")
        mystring.append("\t\t\t\t<city>" + data["crises"][crisis].info.loc.city + "</city>\n")
        mystring.append("\t\t\t\t<region>" + data["crises"][crisis].info.loc.region + "</region>\n")
        mystring.append("\t\t\t\t<country>" + data["crises"][crisis].info.loc.country + "</country>\n")
        myString.append("\t\t\t</loc>\n")
        myString.append("\t\t\t<impact>\n")
        myString.append("\t\t\t\t<human>\n")
        mystring.append("\t\t\t\t\t<deaths>" + data["crises"][crisis].info.impact.human.deaths + "</deaths>\n")
        mystring.append("\t\t\t\t\t<displaced>" + data["crises"][crisis].info.impact.human.displaced + "</displaced>\n")
        mystring.append("\t\t\t\t\t<injured>" + data["crises"][crisis].info.impact.human.injured + "</injured>\n")
        mystring.append("\t\t\t\t\t<missing>" + data["crises"][crisis].info.impact.human.missing + "</missing>\n")
        mystring.append("\t\t\t\t\t<misc>" + data["crises"][crisis].info.impact.human.misc + "</misc>\n")
        myString.append("\t\t\t\t</human>\n")
        myString.append("\t\t\t\t<economic>\n")
        mystring.append("\t\t\t\t\t<amount>" + data["crises"][crisis].info.impact.economic.amount + "</amount>\n")
        mystring.append("\t\t\t\t\t<currency>" + data["crises"][crisis].info.impact.economic.currency + "</currency>\n")
        mystring.append("\t\t\t\t\t<misc>" + data["crises"][crisis].info.impact.economic.misc + "</misc>\n")
        myString.append("\t\t\t\t</economic>\n")
        myString.append("\t\t\t</impact>\n")
        myString.append("\t\t</info>\n")
        myString.append("\t\t<ref>\n")
        myString.append("\t\t\t<primaryImage>\n")
        mystring.append("\t\t\t\t<site>" + data["crises"][crisis].ref.primaryImage.site + "</site>\n")
        mystring.append("\t\t\t\t<title>" + data["crises"][crisis].ref.primaryImage.title + "</title>\n")
        mystring.append("\t\t\t\t<url>" + data["crises"][crisis].ref.primaryImage.url + "</url>\n")
        mystring.append("\t\t\t\t<description>" + data["crises"][crisis].ref.primaryImage.description + "</description>\n")
        myString.append("\t\t\t</primaryImage>\n")
        for image in data["crises"][crisis].ref.images
        	myString.append("\t\t\t<image>\n")
        	mystring.append("\t\t\t\t<site>" + data["crises"][crisis].ref.image.site + "</site>\n")
        	mystring.append("\t\t\t\t<title>" + data["crises"][crisis].ref.image.title + "</title>\n")
        	mystring.append("\t\t\t\t<url>" + data["crises"][crisis].ref.image.url + "</url>\n")
        	mystring.append("\t\t\t\t<description>" + data["crises"][crisis].ref.image.description + "</description>\n")
        	myString.append("\t\t\t</image>\n")
        for video in data["crises"][crisis].ref.videos
        	myString.append("\t\t\t<video>\n")
        	mystring.append("\t\t\t\t<site>" + data["crises"][crisis].ref.video.site + "</site>\n")
        	mystring.append("\t\t\t\t<title>" + data["crises"][crisis].ref.video.title + "</title>\n")
        	mystring.append("\t\t\t\t<url>" + data["crises"][crisis].ref.video.url + "</url>\n")
        	mystring.append("\t\t\t\t<description>" + data["crises"][crisis].ref.video.description + "</description>\n")
        	myString.append("\t\t\t</video>\n")
        for social in data["crises"][crisis].ref.socials
        	myString.append("\t\t\t<social>\n")
        	mystring.append("\t\t\t\t<site>" + data["crises"][crisis].ref.social.site + "</site>\n")
        	mystring.append("\t\t\t\t<title>" + data["crises"][crisis].ref.social.title + "</title>\n")
        	mystring.append("\t\t\t\t<url>" + data["crises"][crisis].ref.social.url + "</url>\n")
        	mystring.append("\t\t\t\t<description>" + data["crises"][crisis].ref.social.description + "</description>\n")
        	myString.append("\t\t\t</social>\n")
        for ext in data["crises"][crisis].ref.exts
        	myString.append("\t\t\t<ext>\n")
        	mystring.append("\t\t\t\t<site>" + data["crises"][crisis].ref.ext.site + "</site>\n")
        	mystring.append("\t\t\t\t<title>" + data["crises"][crisis].ref.ext.title + "</title>\n")
        	mystring.append("\t\t\t\t<url>" + data["crises"][crisis].ref.ext.url + "</url>\n")
        	mystring.append("\t\t\t\t<description>" + data["crises"][crisis].ext.social.description + "</description>\n")
        	myString.append("\t\t\t</ext>\n")
        myString.append("\t\t</ref>\n")
        mystring.append("\t\t<misc>" + data["crises"][crisis].misc + "</misc>\n")
        for orgs in data["crises"][crisis].org
        	myString.append("\t\t<org " #...
        	#..
        for person in data["crises"][crisis]
        	myString.append(...)
        
        myString += "\t<\crisis>\n"
        
    for org in data["orgs"]:
        myString += "\t<org>\n"
        
        myString += "\t<\org>\n"
        
    for person in data["people"]:
        myString += "\t<person>\n"
        
        myString += "\t<\person>\n"
    
    myString += "</worldCrises>"
    return myString

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
                                            ('/export', ExportHandler)
                                         ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

