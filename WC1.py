import xml.etree.ElementTree as ET

import wsgiref.handlers

from google.appengine.ext import webapp



class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'

    inFile = open("htmlgoodies/mockup.html", 'r')
    outstr = inFile.read() #"HELLO CAR RAMROD"
    inFile.close()
    
    self.response.out.write(outstr)

def read(filename):
  tree = ET.ElementTree(file='WC_orig.xml')
  #tree = ET.parse(filename)
  root = tree.getroot()
  
  #f = open("wc.out", 'w')
  
  for child_of_root in root:
    print child_of_root.tag, child_of_root.attrib
  
  tree = ET.parse('WC_orig.xml')
  
  
  
  #print "read complete"
  
  
  #children = root.getchildren()
  
  #f = open("wc.out", 'w')
  #f.write(elem)
  #w = "wc.out"
  #w.write(' '.join([str(tree[k]) for k in xrange(lenTree)]))
  
  #elem = tree.getroot()

def main():
  read("WC.xml")
  application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)


"""
to run:
google_appengine/dev_appserver.py cs373-wc/
http://localhost:8080/
"""
