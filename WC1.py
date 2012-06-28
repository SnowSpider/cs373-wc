import wsgiref.handlers
import xml.etree.cElementTree as ET
from google.appengine.ext import webapp
import logging

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'

    inFile = open("htmlgoodies/mockup.html", 'r')
    outstr = inFile.read() #"HELLO CAR RAMROD"
    inFile.close()
    ImportXml("WC.xml")
    self.response.out.write(outstr)


def ImportXml(filename):
  tree = ET.parse(filename)
  node = tree.find('./with_attributes')
  logging.debug( node.tag)
  for name, value in sorted(node.attrib.items()):
      logging.debug((name,value))
  logging.debug("")   

def main():
  
  application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)
