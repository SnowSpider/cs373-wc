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

# Third party package django was enabled in app.yaml but not found on import. You may have to download and install it.

data_models = []

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
    mail = db.ReferenceProperty(FullAddress)
    
class HumanImpact(db.Model):
    deaths = db.IntegerProperty()
    displaced = db.IntegerProperty()
    injured = db.IntegerProperty()
    missing = db.IntegerProperty()
    misc = db.StringProperty()

class EconomicImpact(db.Model):
    amount = db.IntegerProperty()
    currency = db.StringProperty()
    misc = db.StringProperty()
    
class Impact(db.Model):
    human = db.ReferenceProperty(HumanImpact)
    economic = db.ReferenceProperty(EconomicImpact)
    
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
    time = db.ReferenceProperty(Date)
    loc = db.ReferenceProperty(Location)
    impact = db.ReferenceProperty(Impact)
    
class OrgInfo(db.Model):
    type_ = db.StringProperty()
    history = db.TextProperty()
    contact = db.ReferenceProperty(ContactInfo)
    loc = db.ReferenceProperty(Location)

class PersonInfo(db.Model):
    type_ = db.StringProperty()
    birthdate = db.ReferenceProperty(Date)
    nationality = db.StringProperty()
    biography = db.TextProperty()
    
class Reference(db.Model):
    primaryImage = db.ReferenceProperty(Link)
    images = db.ListProperty(db.Key)
    videos = db.ListProperty(db.Key)
    socials = db.ListProperty(db.Key)
    exts = db.ListProperty(db.Key)
    
class Crisis(db.Model):
    idref = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    info = db.ReferenceProperty(CrisisInfo)
    ref = db.ReferenceProperty(Reference)
    misc = db.StringProperty()
    relatedOrgs = db.StringListProperty()
    relatedPeople = db.StringListProperty()
    
class Organization(db.Model):
    idref = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    info = db.ReferenceProperty(OrgInfo)
    ref = db.ReferenceProperty(Reference)
    misc = db.StringProperty()
    relatedCrises = db.StringListProperty()
    relatedPeople = db.StringListProperty()
    
class Person(db.Model):
    idref = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    info = db.ReferenceProperty(PersonInfo)
    ref = db.ReferenceProperty(Reference)
    misc = db.StringProperty()
    relatedCrises = db.StringListProperty()
    relatedOrgs = db.StringListProperty()

class WorldCrises(db.Model):
    crises = db.ListProperty(db.Key)
    orgs = db.ListProperty(db.Key)
    people = db.ListProperty(db.Key)
    
    
class MainHandler(webapp.RequestHandler):
    def get(self):
        """
        This method is called by the GAE when a user navigates to the root page.
        It draws the page.
        """
        path = self.request.path

        crises = Crisis.all().fetch(50)
        orgs = Organization.all().fetch(50)
        people = Person.all().fetch(50)    
   
        #crises = data_models['crises'].values()
        #orgs = data_models['orgs'].values()
        #people = data_models['people'].values() 

        template_values = {
            'crises': crises,
            'people': people,
            'orgs': orgs,
        }

        self.response.headers['Content-Type'] = 'text/html'

        if path.startswith("/crises/") :
            crisis = Crisis.gql("WHERE idref = :1", path[8:]).fetch(1)
            if crisis: 
                template_values['crisis'] = crisis[0]
                self.response.out.write(str(template.render('djangogoodies/crisistemplate.html', template_values)))
            else:
                self.response.out.write("No such crisis!")
        elif path.startswith("/organizations/") :
            org = Organization.gql("WHERE idref = :1", path[15:]).fetch(1)
            if org: 
                template_values['org'] = org[0]
                self.response.out.write(str(template.render('djangogoodies/organizationtemplate.html', template_values)))
            else:
                self.response.out.write("No such organization!")
        elif path.startswith("/people/"):
            person = Person.gql("WHERE idref = :1", path[8:]).fetch(1)
            if person: 
                template_values['person'] = person[0]
                self.response.out.write(str(template.render('djangogoodies/persontemplate.html', template_values)))
            else:
                self.response.out.write("No such person!")
        else:
            self.response.out.write(str(template.render('djangogoodies/maintemplate.html', template_values)))
            #inFile = open("htmlgoodies/mockup.html", 'r')
            #outstr = inFile.read() #"HELLO CAR RAMROD"
            #inFile.close()
            #self.response.out.write(outstr)

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
            self.response.out.write("<script type=\"text/javascript\">")
            self.response.out.write("parent.location.reload();")
            self.response.out.write("</script>")
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

# ----
# xstr
# ----

def xstr(e):
    """
    Accpets an XML element and returns a string
    e the element to be converted to string
    return None if e was None, int otherwise
    """
    return None if e is None else e.text

# -----
# xint
# -----

def xint(e):
    """
    Accpets an XML element and returns an int
    e the element to be converted to int
    return 0 if e was None, int otherwise
    """
    temp = xstr(e)
    return 0 if temp is None else int(temp)

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

# ----
# trim
# ----

def trim(s):
    """
    Takes a string, eliminates None and calls fixAmp
    s the string to be trimmed
    return the trimmed string
    """
    return "" if s is None else fixAmp(str(s))

# -----------
# import_file
# -----------
def import_file(xml_file):
    tree = ET.ElementTree(file = xml_file)
    root = tree.getroot()
    
    data = []
    
    crises = root.findall("crisis")
    for crisis in crises: 
        crisis_model = Crisis(key_name = crisis.attrib["id"], 
                              idref = crisis.attrib["id"], 
                              name = crisis.find("name").text)
                              
        info = crisis.find("info")
        info_model = CrisisInfo(history = xstr(info.find("history")), 
                                help = xstr(info.find("help")), 
                                resources = xstr(info.find("resources")), 
                                type_ = xstr(info.find("type")))
                                
        time = info.find("time")
        time_model = Date(time = xstr(time.find("time")), 
                          day = xint(time.find("day")), 
                          month = xint(time.find("month")), 
                          year = xint(time.find("year")), 
                          misc = xstr(time.find("misc")))
        time_model.put()
        info_model.time = time_model
        
        loc = info.find("loc")
        loc_model = Location(city = xstr(loc.find("city")), 
                             region = xstr(loc.find("region")), 
                             country = xstr(loc.find("country")))
        loc_model.put()
        
        info_model.loc = loc_model
        impact = info.find("impact")
        
        human = impact.find("human")
        human_model = HumanImpact(deaths = xint(human.find("deaths")), 
                                  displaced = xint(human.find("displaced")), 
                                  injured = xint(human.find("injured")), 
                                  missing = xint(human.find("missing")), 
                                  misc = xstr(human.find("misc")))
        human_model.put() #saves the model
        
        economic = impact.find("economic")
        economic_model = EconomicImpact(amount = xint(human.find("amount")), 
                                        currency = xstr(human.find("currency")), 
                                        misc = xstr(human.find("misc")))
        economic_model.put()
        impact_model = Impact(human = human_model, economic = economic_model)
        impact_model.put()
        
        info_model.impact = impact_model
        info_model.put()
        crisis_model.info = info_model
        
        ref = crisis.find("ref")
        primaryImage = ref.find("primaryImage")
        ref_model = Reference()
        pimage_model = Link(site = xstr(primaryImage.find("site")), 
                            title = xstr(primaryImage.find("title")), 
                            url = xstr(primaryImage.find("url")), 
                            description = xstr(primaryImage.find("description")))
        pimage_model.put()
        ref_model.primaryImage = pimage_model
        images = ref.findall("image")
        for image in images:
            link_model = Link(site = xstr(image.find("site")), 
                              title = xstr(image.find("title")), 
                              url = xstr(image.find("url")), 
                              description = xstr(image.find("description")))
            link_model.put()
            ref_model.images.append(link_model.key())
        videos = ref.findall("video")
        for video in videos:
            link_model = Link(site = xstr(video.find("site")), 
                              title = xstr(video.find("title")), 
                              url = xstr(video.find("url")), 
                              description = xstr(video.find("description")))
            link_model.put()
            ref_model.videos.append(link_model.key())
        socials = ref.findall("social") 
        for social in socials:
            link_model = Link(site = xstr(social.find("site")), 
                              title = xstr(social.find("title")), 
                              url = xstr(social.find("url")), 
                              description = xstr(social.find("description")))
            link_model.put()
            ref_model.socials.append(link_model.key())
        exts = ref.findall("ext")
        for ext in exts:
            link_model = Link(site = xstr(ext.find("site")), 
                              title = xstr(ext.find("title")), 
                              url = xstr(ext.find("url")), 
                              description = xstr(ext.find("description")))
            link_model.put()
            ref_model.exts.append(link_model.key())
        ref_model.put()
        crisis_model.ref = ref_model
        
        crisis_model.misc = xstr(crisis.find("misc"))
        
        relatedOrgs = crisis.findall("org")
        for relatedOrg in relatedOrgs:
            crisis_model.relatedOrgs.append(relatedOrg.attrib["idref"])
        relatedPeople = crisis.findall("person")
        for relatedPerson in relatedPeople:
            crisis_model.relatedPeople.append(relatedPerson.attrib["idref"])
        
        
        crisis_model.put()
        data.append(crisis_model)
    
    orgs = root.findall("organization")
    for org in orgs: 
        org_model = Organization(key_name = org.attrib["id"], idref = org.attrib["id"], name = org.find("name").text)
        
        info = org.find("info")
        info_model = OrgInfo(type_ = xstr(info.find("type")), 
                             history = xstr(info.find("history")))
        contact = info.find("contact")
        
        contact_model = ContactInfo(phone = xstr(contact.find("phone")), 
                                    email = xstr(contact.find("email")))
        mail = contact.find("mail")
        mail_model = FullAddress(addr = xstr(mail.find("address")), 
                                 city = xstr(mail.find("city")), 
                                 state = xstr(mail.find("state")), 
                                 country = xstr(mail.find("country")), 
                                 zip_ = xstr(mail.find("zip")))
        mail_model.put()
        contact_model.mail = mail_model
        
        contact_model.put()
        info_model.contact = contact_model
        
        
        loc = info.find("loc")
        loc_model = Location(city = xstr(loc.find("city")), 
                             region = xstr(loc.find("region")), 
                             country = xstr(loc.find("country")))
        loc_model.put()
        info_model.loc = loc_model
        
        info_model.put()
        org_model.info = info_model
        
        ref = org.find("ref")
        primaryImage = ref.find("primaryImage")
        ref_model = Reference()
        pimage_model = Link(site = xstr(primaryImage.find("site")), 
                            title = xstr(primaryImage.find("title")), 
                            url = xstr(primaryImage.find("url")), 
                            description = xstr(primaryImage.find("description")))
        pimage_model.put()
        ref_model.primaryImage = pimage_model
        images = ref.findall("image")
        for image in images:
            link_model = Link(site = xstr(image.find("site")), 
                              title = xstr(image.find("title")), 
                              url = xstr(image.find("url")), 
                              description = xstr(image.find("description")))
            link_model.put()
            ref_model.images.append(link_model.key())
        videos = ref.findall("video")
        for video in videos:
            link_model = Link(site = xstr(video.find("site")), 
                              title = xstr(video.find("title")), 
                              url = xstr(video.find("url")), 
                              description = xstr(video.find("description")))
            link_model.put()
            ref_model.videos.append(link_model.key())
        socials = ref.findall("social") 
        for social in socials:
            link_model = Link(site = xstr(social.find("site")), 
                              title = xstr(social.find("title")), 
                              url = xstr(social.find("url")), 
                              description = xstr(social.find("description")))
            link_model.put()
            ref_model.socials.append(link_model.key())
        exts = ref.findall("ext")
        for ext in exts:
            link_model = Link(site = xstr(ext.find("site")), 
                              title = xstr(ext.find("title")), 
                              url = xstr(ext.find("url")), 
                              description = xstr(ext.find("description")))
            link_model.put()
            ref_model.exts.append(link_model.key())
        ref_model.put()
        org_model.ref = ref_model.key()
        
        org_model.misc = xstr(org.find("misc"))
        
        relatedCrises = org.findall("crisis")
        for relatedCrisis in relatedCrises:
            org_model.relatedCrises.append(relatedCrisis.attrib["idref"])
        relatedPeople = org.findall("person")
        for relatedPerson in relatedPeople:
            org_model.relatedPeople.append(relatedPerson.attrib["idref"])
        
        
        org_model.put()
        data.append(org_model)
        
    people = root.findall("person")
    for person in people: 
        person_model = Person(key_name = person.attrib["id"], idref = person.attrib["id"], name = person.find("name").text)
        info = person.find("info")
        
        info = person.find("info")
        info_model = PersonInfo(type_ = xstr(info.find("type")), 
                                nationality = xstr(info.find("nationality")), 
                                biography = xstr(info.find("biography")))
        
        birthdate = info.find("birthdate")
        birthdate_model = Date(time = xstr(birthdate.find("time")), 
                               day = xint(birthdate.find("day")), 
                               month = xint(birthdate.find("month")), 
                               year = xint(birthdate.find("year")), 
                               misc = xstr(birthdate.find("misc")))
        birthdate_model.put()
        info_model.birthdate = birthdate_model
        
        info_model.put()
        person_model.info = info_model.key()
        
        ref = person.find("ref")
        primaryImage = ref.find("primaryImage")
        ref_model = Reference()
        pimage_model = Link(site = xstr(primaryImage.find("site")), 
                            title = xstr(primaryImage.find("title")), 
                            url = xstr(primaryImage.find("url")), 
                            description = xstr(primaryImage.find("description")))
        pimage_model.put()
        ref_model.primaryImage = pimage_model
        images = ref.findall("image")
        for image in images:
            link_model = Link(site = xstr(image.find("site")), 
                              title = xstr(image.find("title")), 
                              url = xstr(image.find("url")), 
                              description = xstr(image.find("description")))
            link_model.put()
            ref_model.images.append(link_model.key())
        videos = ref.findall("video")
        for video in videos:
            link_model = Link(site = xstr(video.find("site")), 
                              title = xstr(video.find("title")), 
                              url = xstr(video.find("url")), 
                              description = xstr(video.find("description")))
            link_model.put()
            ref_model.videos.append(link_model.key())
        socials = ref.findall("social") 
        for social in socials:
            link_model = Link(site = xstr(social.find("site")), 
                              title = xstr(social.find("title")), 
                              url = xstr(social.find("url")), 
                              description = xstr(social.find("description")))
            link_model.put()
            ref_model.socials.append(link_model.key())
        exts = ref.findall("ext")
        for ext in exts:
            link_model = Link(site = xstr(ext.find("site")), 
                              title = xstr(ext.find("title")), 
                              url = xstr(ext.find("url")), 
                              description = xstr(ext.find("description")))
            link_model.put()
            ref_model.exts.append(link_model.key())
        ref_model.put()
        person_model.ref = ref_model.key()        
        
        person_model.misc = xstr(person.find("misc"))
        
        relatedCrises = person.findall("crisis")
        for relatedCrisis in relatedCrises:
            person_model.relatedCrises.append(relatedCrisis.attrib["idref"])
        relatedOrgs = person.findall("org")
        for relatedOrg in relatedOrgs:
            person_model.relatedOrgs.append(relatedOrg.attrib["idref"])
        
        
        person_model.put()
        data.append(person_model)
    
    return data

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
    
    for thing in data:
        if type(thing) is Crisis:
            myString.append("\t<crisis id=\"" + trim(thing.idref) + "\">\n")
            myString.append("\t\t<name>" + trim(thing.name) + "</name>\n")
            myString.append("\t\t<info>\n")
            myString.append("\t\t\t<history>" + trim(thing.info.history) + "</history>\n")
            myString.append("\t\t\t<help>" + trim(thing.info.help) + "</help>\n")
            myString.append("\t\t\t<resources>" + trim(thing.info.resources) + "</resources>\n")
            myString.append("\t\t\t<type>" + trim(thing.info.type_) + "</type>\n")
            myString.append("\t\t\t<time>\n")
            myString.append("\t\t\t\t<time>" + trim(thing.info.time.time) + "</time>\n")
            myString.append("\t\t\t\t<day>" + trim(thing.info.time.day) + "</day>\n")
            myString.append("\t\t\t\t<month>" + trim(thing.info.time.month) + "</month>\n")
            myString.append("\t\t\t\t<year>" + trim(thing.info.time.year) + "</year>\n")
            myString.append("\t\t\t\t<misc>" + trim(thing.info.time.misc) + "</misc>\n")
            myString.append("\t\t\t</time>\n")
            myString.append("\t\t\t<loc>\n")
            myString.append("\t\t\t\t<city>" + trim(thing.info.loc.city) + "</city>\n")
            myString.append("\t\t\t\t<region>" + trim(thing.info.loc.region) + "</region>\n")
            myString.append("\t\t\t\t<country>" + trim(thing.info.loc.country) + "</country>\n")
            myString.append("\t\t\t</loc>\n")
            myString.append("\t\t\t<impact>\n")
            myString.append("\t\t\t\t<human>\n")
            myString.append("\t\t\t\t\t<deaths>" + trim(thing.info.impact.human.deaths) + "</deaths>\n")
            myString.append("\t\t\t\t\t<displaced>" + trim(thing.info.impact.human.displaced) + "</displaced>\n")
            myString.append("\t\t\t\t\t<injured>" + trim(thing.info.impact.human.injured) + "</injured>\n")
            myString.append("\t\t\t\t\t<missing>" + trim(thing.info.impact.human.missing) + "</missing>\n")
            myString.append("\t\t\t\t\t<misc>" + trim(thing.info.impact.human.misc) + "</misc>\n")
            myString.append("\t\t\t\t</human>\n")
            myString.append("\t\t\t\t<economic>\n")
            myString.append("\t\t\t\t\t<amount>" + trim(thing.info.impact.economic.amount) + "</amount>\n")
            myString.append("\t\t\t\t\t<currency>" + trim(thing.info.impact.economic.currency) + "</currency>\n")
            myString.append("\t\t\t\t\t<misc>" + trim(thing.info.impact.economic.misc) + "</misc>\n")
            myString.append("\t\t\t\t</economic>\n")
            myString.append("\t\t\t</impact>\n")
            myString.append("\t\t</info>\n")
            myString.append("\t\t<ref>\n")
            myString.append("\t\t\t<primaryImage>\n")
            myString.append("\t\t\t\t<site>" + trim(thing.ref.primaryImage.site) + "</site>\n")
            myString.append("\t\t\t\t<title>" + trim(thing.ref.primaryImage.title) + "</title>\n")
            myString.append("\t\t\t\t<url>" + trim(thing.ref.primaryImage.url) + "</url>\n")
            myString.append("\t\t\t\t<description>" + trim(thing.ref.primaryImage.description) + "</description>\n")
            myString.append("\t\t\t</primaryImage>\n")
            for image in thing.ref.images:
                myString.append("\t\t\t<image>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(image).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(image).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(image).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(image).description) + "</description>\n")
                myString.append("\t\t\t</image>\n")
            for video in thing.ref.videos:
                myString.append("\t\t\t<video>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(video).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(video).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(video).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(video).description) + "</description>\n")
                myString.append("\t\t\t</video>\n")
            for social in thing.ref.socials:
                myString.append("\t\t\t<social>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(social).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(social).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(social).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(social).description) + "</description>\n")
                myString.append("\t\t\t</social>\n")
            for ext in thing.ref.exts:
                myString.append("\t\t\t<ext>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(ext).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(ext).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(ext).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(ext).description) + "</description>\n")
                myString.append("\t\t\t</ext>\n")
            myString.append("\t\t</ref>\n")
            myString.append("\t\t<misc>" + trim(thing.misc) + "</misc>\n")
            for org in thing.relatedOrgs: 
                assert org is not None
                myString.append("\t\t<org idref=\"" + org + "\"></org>\n")
            for person in thing.relatedPeople:
                assert person is not None
                myString.append("\t\t<person idref=\"" + person + "\"></person>\n")
            myString.append("\t</crisis>\n")
        
        elif type(thing) is Organization:
            myString.append("\t<organization id=\""+thing.idref+"\">\n")
            myString.append("\t\t<name>" + trim(thing.name) + "</name>\n")
            myString.append("\t\t<info>\n")
            myString.append("\t\t\t<type>" + trim(thing.info.type_) + "</type>\n")
            myString.append("\t\t\t<history>" + trim(thing.info.history) + "</history>\n")
            myString.append("\t\t\t<contact>\n")
            myString.append("\t\t\t\t<phone>" + trim(thing.info.contact.phone) + "</phone>\n")
            myString.append("\t\t\t\t<email>" + trim(thing.info.contact.email) + "</email>\n")
            myString.append("\t\t\t\t<mail>\n")
            myString.append("\t\t\t\t\t<address>" + trim(thing.info.contact.mail.address) + "</address>\n")
            myString.append("\t\t\t\t\t<city>" + trim(thing.info.contact.mail.city) + "</city>\n")
            myString.append("\t\t\t\t\t<state>" + trim(thing.info.contact.mail.state) + "</state>\n")
            myString.append("\t\t\t\t\t<country>" + trim(thing.info.contact.mail.country) + "</country>\n")
            myString.append("\t\t\t\t\t<zip>" + trim(thing.info.contact.mail.zip_) + "</zip>\n")
            myString.append("\t\t\t\t</mail>\n")
            myString.append("\t\t\t</contact>\n")
            myString.append("\t\t\t<loc>\n")
            myString.append("\t\t\t\t<city>" + trim(thing.info.loc.city) + "</city>\n")
            myString.append("\t\t\t\t<region>" + trim(thing.info.loc.region) + "</region>\n")
            myString.append("\t\t\t\t<country>" + trim(thing.info.loc.country) + "</country>\n")
            myString.append("\t\t\t</loc>\n")
            myString.append("\t\t</info>\n")
            myString.append("\t\t<ref>\n")
            myString.append("\t\t\t<primaryImage>\n")
            myString.append("\t\t\t\t<site>" + trim(thing.ref.primaryImage.site) + "</site>\n")
            myString.append("\t\t\t\t<title>" + trim(thing.ref.primaryImage.title) + "</title>\n")
            myString.append("\t\t\t\t<url>" + trim(thing.ref.primaryImage.url) + "</url>\n")
            myString.append("\t\t\t\t<description>" + trim(thing.ref.primaryImage.description) + "</description>\n")
            myString.append("\t\t\t</primaryImage>\n")
            for image in thing.ref.images:
                myString.append("\t\t\t<image>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(image).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(image).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(image).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(image).description) + "</description>\n")
                myString.append("\t\t\t</image>\n")
            for video in thing.ref.videos:
                myString.append("\t\t\t<video>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(video).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(video).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(video).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(video).description) + "</description>\n")
                myString.append("\t\t\t</video>\n")
            for social in thing.ref.socials:
                myString.append("\t\t\t<social>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(social).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(social).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(social).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(social).description) + "</description>\n")
                myString.append("\t\t\t</social>\n")
            for ext in thing.ref.exts:
                myString.append("\t\t\t<ext>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(ext).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(ext).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(ext).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(ext).description) + "</description>\n")
                myString.append("\t\t\t</ext>\n")
            myString.append("\t\t</ref>\n")
            myString.append("\t\t<misc>" + trim(thing.misc) + "</misc>\n")
            for crisis in thing.relatedCrises: 
                myString.append("\t\t<crisis idref=\"" + crisis + "\"></crisis>\n")
            for person in thing.relatedPeople:
                myString.append("\t\t<person idref=\"" + person + "\"></person>\n")
            myString.append("\t</organization>\n")
        
        elif type(thing) is Person:
            myString.append("\t<person id=\""+thing.idref+"\">\n")
            myString.append("\t\t<name>" + trim(thing.name) + "</name>\n")
            myString.append("\t\t<info>\n")
            myString.append("\t\t\t<type>" + trim(thing.info.type_) + "</type>\n")
            myString.append("\t\t\t<birthdate>\n")
            myString.append("\t\t\t\t<time>" + trim(thing.info.birthdate.time) + "</time>\n")
            myString.append("\t\t\t\t<day>" + trim(thing.info.birthdate.day) + "</day>\n")
            myString.append("\t\t\t\t<year>" + trim(thing.info.birthdate.year) + "</year>\n")
            myString.append("\t\t\t\t<misc>" + trim(thing.info.birthdate.misc) + "</misc>\n")
            myString.append("\t\t\t</birthdate>\n")
            myString.append("\t\t\t<nationality>" + trim(thing.info.nationality) + "</nationality>\n")
            myString.append("\t\t\t<biography>" + trim(thing.info.biography) + "</biography>\n")
            myString.append("\t\t</info>\n")
            myString.append("\t\t<ref>\n")
            myString.append("\t\t\t<primaryImage>\n")
            myString.append("\t\t\t\t<site>" + trim(thing.ref.primaryImage.site) + "</site>\n")
            myString.append("\t\t\t\t<title>" + trim(thing.ref.primaryImage.title) + "</title>\n")
            myString.append("\t\t\t\t<url>" + trim(thing.ref.primaryImage.url) + "</url>\n")
            myString.append("\t\t\t\t<description>" + trim(thing.ref.primaryImage.description) + "</description>\n")
            myString.append("\t\t\t</primaryImage>\n")
            for image in thing.ref.images:
                myString.append("\t\t\t<image>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(image).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(image).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(image).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(image).description) + "</description>\n")
                myString.append("\t\t\t</image>\n")
            for video in thing.ref.videos:
                myString.append("\t\t\t<video>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(video).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(video).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(video).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(video).description) + "</description>\n")
                myString.append("\t\t\t</video>\n")
            for social in thing.ref.socials:
                myString.append("\t\t\t<social>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(social).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(social).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(social).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(social).description) + "</description>\n")
                myString.append("\t\t\t</social>\n")
            for ext in thing.ref.exts:
                myString.append("\t\t\t<ext>\n")
                myString.append("\t\t\t\t<site>" + trim(db.get(ext).site) + "</site>\n")
                myString.append("\t\t\t\t<title>" + trim(db.get(ext).title) + "</title>\n")
                myString.append("\t\t\t\t<url>" + trim(db.get(ext).url) + "</url>\n")
                myString.append("\t\t\t\t<description>" + trim(db.get(ext).description) + "</description>\n")
                myString.append("\t\t\t</ext>\n")
            myString.append("\t\t</ref>\n")
            myString.append("\t\t<misc>" + trim(thing.misc) + "</misc>\n")
            for crisis in thing.relatedCrises: 
                myString.append("\t\t<crisis idref=\"" + crisis + "\"></crisis>\n")
            for org in thing.relatedOrgs: 
                myString.append("\t\t<org idref=\"" + org + "\"></org>\n")
            myString.append("\t</person>\n")
        
    myString.append("</worldCrises>")
    
    debug("".join(myString))
    
    return "".join(myString)

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

