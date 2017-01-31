#!/usr/bin/env python
# this script parse the TV listing xml for kodi addon to AppleTV addon format


import sys
import urlparse
import urllib2
import xml.dom.minidom


#listing URL
#default if didn't get passed in fromt the cmdline arg
listUrl = "http://pastebin.com/raw/tMz6iwjK"
fileName = "TVListing.txt"

#check if there is arg to override the listing URL
if (len(sys.argv)>1):
    listUrl = sys.argv[1]

def get_dom():
    proxy = urllib2.ProxyHandler({'http': 'adc-proxy.oracle.com'})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    return xml.dom.minidom.parse(urllib2.urlopen(listUrl))

file = open(fileName, 'w')
#print the to the file
for cat in get_dom().getElementsByTagName('class'):
    for ch in cat.getElementsByTagName('channel'):
        tvTitle = ch.getAttribute('name')
        tvTitle = tvTitle.replace(' ', '')
        tvLink = ch.getElementsByTagName('tvlink')
        if not tvLink:
            continue
        #file.write(tvTitle.encode('utf8'))
        file.write("{0} {1} {2}\n".format(tvTitle.encode('utf8'), tvLink[0].getAttribute('link').encode('utf8'), cat.getAttribute('classname').encode('utf8')))

file.close()
