import wsgiref.handlers
import xml.etree.cElementTree as ET
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import logging

data_models = {"people":[], "crises":[], "orgs":[]}

class ContactInfo(db.Model):
    phone_number = db.PhoneNumberProperty()
    email = db.EmailProperty()
    address = db.TextProperty()

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
    #contact_info = ContactInfo()
    contact_info = None
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
        """
        This method is called by the GAE when a user navigates to the root page.
        It draws the page.
        """
        self.response.headers['Content-Type'] = 'text/html'

        inFile = open("htmlgoodies/mockup.html", 'r')
        outstr = inFile.read() #"HELLO CAR RAMROD"
        inFile.close()
        imported = ImportXml("WC.xml")
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

#Assumes valid xml instance
def ImportXml(filename):
    """
    Imports data from an xml instance and saves it in heap
    filename the name of the .xml file
    return the desired data in multi-dimensional dictionary
    """
    return import_file(open(filename, "r"))

def import_file(xml_file):
    tree = ET.ElementTree(file = xml_file)
    root = tree.getroot()
    #debug(root)
    #debug("HIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
    imported = {"people": {}, "crises": {}, "orgs": {}}
    #debug(imported)
    people = root.find("people").findall("person")
    #debug(people)
    for person in people :
        person_model = Person(name = person.find("name").text)
        
        kind_ = person.find("kind")
        if kind_ is not None:
            person_model.kind_ = kind_.text
        
        location = person.find("location")
        if location is not None:
            person_model.location = location.text
        
        history = person.find("history")
        if history is not None:
            person_model.history = history.text
        
        images = person.find("images")
        if images is not None:
            #counter = 0
            #for image in images.findall("link") :
            #    person_model.images.append(db.Link(image.text))   
            person_model.images = map(lambda e: db.Link(e.text), images.findall("link"))
    
        videos = person.find("videos")
        if videos is not None:
            person_model.videos = map(lambda e: db.Link(e.text), videos.findall("link"))
    
        social_networks = person.find("social_networks")
        if social_networks is not None:
            person_model.social_networks = map(lambda e: db.Link(e.text), social_networks.findall("link"))
    
        external_links = person.find("external_links")
        if external_links is not None:
            person_model.external_links = map(lambda e: db.Link(e.text), external_links.findall("link"))

        related_crises = person.find("related_crises")
        if related_crises is not None:
            person_model.related_crises = map(lambda e: e.text, related_crises.findall("crisisRef"))
    
        related_orgs = person.find("related_orgs")
        if related_orgs is not None:
            person_model.related_orgs = map(lambda e: e.text, related_orgs.findall("orgRef"))
        imported["people"][person_model.name] = person_model

    crises = root.find("crises").findall("crisis")
    for crisis in crises:
        crisis_model = Crisis(name = crisis.find("name").text)
        kind_ = crisis.find("kind")
        if kind_ is not None:
            crisis_model.kind_ = kind_.text
        
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
            crisis_model.images = map(lambda e: db.Link(e.text), images.findall("link"))
    
        videos = crisis.find("videos")
        if videos is not None:
            crisis_model.videos = map(lambda e: db.Link(e.text), videos.findall("link"))
    
        social_networks = crisis.find("social_networks")
        if social_networks is not None:
            crisis_model.social_networks = map(lambda e: db.Link(e.text), social_networks.findall("link"))
    
        external_links = crisis.find("external_links")
        if external_links is not None:
            crisis_model.external_links = map(lambda e: db.Link(e.text), external_links.findall("link"))

        related_people = crisis.find("related_people")
        if related_people is not None:
            crisis_model.related_people = map(lambda e: e.text, related_people.findall("personRef"))
    
        related_orgs = crisis.find("related_orgs")
        if related_orgs is not None:
            crisis_model.related_orgs = map(lambda e: e.text, related_orgs.findall("orgRef"))
        imported["crises"][crisis_model.name] = crisis_model
  
    orgs = root.find("orgs").findall("org")
    #debug(len(orgs))
    for org in orgs :
        org_model = Organization(name = org.find("name").text)
    
        kind_ = org.find("kind")
        if kind_ is not None:
            org_model.kind_ = kind_.text
        
        location = org.find("location")
        if location is not None:
            org_model.location = location.text
        
        history = org.find("history")
        if history is not None:
            org_model.history = history.text

        contact_info = org.find("contact_info")
        if contact_info is not None:
            contact_info_model = ContactInfo()
            email = contact_info.find("email")
            if email is not None:
                contact_info_model.email = db.Email(email.text)
            phone_number = contact_info.find("phone_number")
            if phone_number is not None:
                contact_info_model.phone_number = db.PhoneNumber(phone_number.text)
            address = contact_info.find("address")
            if address is not None:
                contact_info_model.address = db.PostalAddress(address.text)
            org_model.contact_info = contact_info_model #!!!
        
        images = org.find("images")
        if images is not None:
            org_model.images = map(lambda e: db.Link(e.text), images.findall("link"))
    
        videos = org.find("videos")
        if videos is not None:
            org_model.videos = map(lambda e: db.Link(e.text), videos.findall("link"))
    
        social_networks = org.find("social_networks")
        if social_networks is not None:
            org_model.social_networks = map(lambda e: db.Link(e.text), social_networks.findall("link"))
    
        external_links = org.find("external_links")
        if external_links is not None:
            org_model.external_links = map(lambda e: db.Link(e.text), external_links.findall("link"))  

        related_crises = org.find("related_crises")
        if related_crises is not None:
            org_model.related_crises = map(lambda e: e.text, related_crises.findall("crisisRef"))
    
        related_people = org.find("related_people")
        if related_people is not None:
            org_model.related_people = map(lambda e: e.text, related_people.findall("personRef"))
        imported["orgs"][org_model.name] = org_model
    #debug(imported)
    
    return imported

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

def ExportXml(data):
    """
    Exports the data to the screen in xml format
    data is the data
    return a string in xml format
    """
    #debug(data)
    myString = "<everything>\n"
    
    myString += "\t<people>\n"
    for person in data["people"]:
        myString += "\t\t<person>\n"
        myString += "\t\t\t<name>" + data["people"][person].name + "</name>\n"
        if data["people"][person].kind_ is not None:
            myString += "\t\t\t<kind>" + data["people"][person].kind_ + "</kind>\n"
        if data["people"][person].location is not None:
            myString += "\t\t\t<location>" + data["people"][person].location + "</location>\n"
        if data["people"][person].history is not None:
            myString += "\t\t\t<history>" + data["people"][person].history + "</history>\n"
        if data["people"][person].images:
            myString += "\t\t\t<images>\n"
            for link in data["people"][person].images:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</images>\n"
        if data["people"][person].videos:
            myString += "\t\t\t<videos>\n"
            for link in data["people"][person].videos:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</videos>\n" 
        if data["people"][person].social_networks:
            myString += "\t\t\t<social_networks>\n"
            for link in data["people"][person].social_networks:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</social_networks>\n"
        if data["people"][person].social_networks:
            myString += "\t\t\t<external_links>\n"
            for link in data["people"][person].external_links:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</external_links>\n"
        if data["people"][person].related_crises:
            myString += "\t\t\t<related_crises>\n"
            for crisis in data["people"][person].related_crises:
                myString += "\t\t\t\t<crisisRef>" + str(crisis) + "</crisisRef>\n"
            myString += "\t\t\t</related_crises>\n"
        if data["people"][person].related_orgs:
            myString += "\t\t\t<related_orgs>\n"
            for org in data["people"][person].related_orgs:
                myString += "\t\t\t\t<orgRef>" + str(org) + "</orgRef>\n"
            myString += "\t\t\t</related_orgs>\n"            
        myString += "\t\t</person>\n"
    myString += "\t</people>\n"
    
    myString += "\t<crises>\n"
    for crisis in data["crises"]:
        myString += "\t\t<crisis>\n"
        myString += "\t\t\t<name>" + data["crises"][crisis].name + "</name>\n"
        if data["crises"][crisis].kind_ is not None:
            myString += "\t\t\t<kind>" + data["crises"][crisis].kind_ + "</kind>\n"
        if data["crises"][crisis].location is not None:
            myString += "\t\t\t<location>" + data["crises"][crisis].location + "</location>\n"
        if data["crises"][crisis].date_and_time is not None:
            myString += "\t\t\t<date_and_time>" + data["crises"][crisis].date_and_time + "</date_and_time>\n"
        if data["crises"][crisis].human_impact is not None:
            myString += "\t\t\t<human_impact>" + data["crises"][crisis].human_impact + "</human_impact>\n"
        if data["crises"][crisis].economic_impact is not None:
            myString += "\t\t\t<economic_impact>" + data["crises"][crisis].economic_impact + "</economic_impact>\n"
        if data["crises"][crisis].resources_needed is not None:
            myString += "\t\t\t<resources_needed>" + data["crises"][crisis].resources_needed + "</resources_needed>\n"
        if data["crises"][crisis].ways_to_help is not None:
            myString += "\t\t\t<ways_to_help>" + data["crises"][crisis].ways_to_help + "</ways_to_help>\n"
        if data["crises"][crisis].history is not None:
            myString += "\t\t\t<history>" + data["crises"][crisis].history + "</history>\n"
        if data["crises"][crisis].images:
            myString += "\t\t\t<images>\n"
            for link in data["crises"][crisis].images:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</images>\n"
        if data["crises"][crisis].videos:
            myString += "\t\t\t<videos>\n"
            for link in data["crises"][crisis].videos:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</videos>\n" 
        if data["crises"][crisis].social_networks:
            myString += "\t\t\t<social_networks>\n"
            for link in data["crises"][crisis].social_networks:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</social_networks>\n"
        if data["crises"][crisis].external_links:
            myString += "\t\t\t<external_links>\n"
            for link in data["crises"][crisis].external_links:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</external_links>\n"
        if data["crises"][crisis].related_orgs:
            myString += "\t\t\t<related_orgs>\n"
            for org in data["crises"][crisis].related_orgs:
                myString += "\t\t\t\t<orgRef>" + str(org) + "</orgRef>\n"
            myString += "\t\t\t</related_orgs>\n"
        if data["crises"][crisis].related_people:
            myString += "\t\t\t<related_people>\n"
            for person in data["crises"][crisis].related_people:
                myString += "\t\t\t\t<personRef>" + str(person) + "</personRef>\n"
            myString += "\t\t\t</related_people>\n"      
        myString += "\t\t</crisis>\n"
    myString += "\t</crises>\n"
    
    myString += "\t<orgs>\n"
    for org in data["orgs"]:
        myString += "\t\t<org>\n"
        myString += "\t\t\t<name>" + data["orgs"][org].name + "</name>\n"
        if data["orgs"][org].kind_ is not None:
            myString += "\t\t\t<kind>" + data["orgs"][org].kind_ + "</kind>\n"
        if data["orgs"][org].location is not None:
            myString += "\t\t\t<location>" + data["orgs"][org].location + "</location>\n"
        
        if data["orgs"][org].history is not None:
            myString += "\t\t\t<history>" + data["orgs"][org].history + "</history>\n"
        
        if data["orgs"][org].contact_info is not None:
            myString += "\t\t\t<contact_info>\n"
            if data["orgs"][org].contact_info.email is not None:
                myString += "\t\t\t\t<email>" + data["orgs"][org].contact_info.email + "</email>\n"
            if data["orgs"][org].contact_info.phone_number is not None:
                myString += "\t\t\t\t<phone_number>" + data["orgs"][org].contact_info.phone_number + "</phone_number>\n"
            if data["orgs"][org].contact_info.address is not None:
                myString += "\t\t\t\t<address>" + data["orgs"][org].contact_info.address + "</address>\n"
            myString += "\t\t\t</contact_info>\n"
        if data["orgs"][org].images:
            myString += "\t\t\t<images>\n"
            for link in data["orgs"][org].images:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</images>\n"
        if data["orgs"][org].videos:
            myString += "\t\t\t<videos>\n"
            for link in data["orgs"][org].videos:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</videos>\n" 
        if data["orgs"][org].social_networks:
            myString += "\t\t\t<social_networks>\n"
            for link in data["orgs"][org].social_networks:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</social_networks>\n"
        if data["orgs"][org].social_networks:
            myString += "\t\t\t<external_links>\n"
            for link in data["orgs"][org].external_links:
                myString += "\t\t\t\t<link>" + str(link) + "</link>\n"
            myString += "\t\t\t</external_links>\n"
        if data["orgs"][org].related_crises:
            myString += "\t\t\t<related_crises>\n"
            for crisis in data["orgs"][org].related_crises:
                myString += "\t\t\t\t<crisisRef>" + str(crisis) + "</crisisRef>\n"
            myString += "\t\t\t</related_crises>\n"
        if data["orgs"][org].related_people:
            myString += "\t\t\t<related_people>\n"
            for person in data["orgs"][org].related_people:
                myString += "\t\t\t\t<personRef>" + str(person) + "</personRef>\n"
            myString += "\t\t\t</related_people>\n"
        myString += "\t\t</org>\n"
    myString += "\t</orgs>\n"
    
    myString += "</everything>"
    
    myString = fixAmp(myString)
    
    debug(myString)
    return myString

def debug(msg):
    logging.debug("\n\n" + str(msg) + "\n")

def main():
    application = webapp.WSGIApplication([  ('/', MainHandler), 
                                            ('/import', ImportFormHandler), 
                                            ('/import_upload', ImportUploadHandler),
                                            ('/export', ExportHandler)
                                         ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
