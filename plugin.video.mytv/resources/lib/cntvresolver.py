# library for handling cntv url
# author: sudoel
import xbmc
import xbmcgui
import traceback
import urllib
import urllib2
import urlparse
try:
	import simplejson as jsonimpl
except ImportError:
	import json as jsonimpl

TIMEOUT_S = 2.0

def showNotification(stringID):
	xbmc.executebuiltin("Notification({0},{1})".format(addon_name, addon.getLocalizedString(stringID)))

def fixURL(tmpurl):
    tmpurl = tmpurl.replace("vtime.cntv.cloudcdn.net:8000", "vtime.cntv.cloudcdn.net") #Global (HDS/FLV) - wrong port
    tmpurl = tmpurl.replace("tv.fw.live.cntv.cn", "tvhd.fw.live.cntv.cn") #China - 403 Forbidden
    return tmpurl

def tryHLSStream(jsondata, subkey):
    print("Trying stream {0}".format(subkey))
    
    if jsondata["hls_url"].has_key(subkey) and jsondata["hls_url"][subkey] != "":
	try:
	    tmpurl = jsondata["hls_url"][subkey]
	    tmpurl = fixURL(tmpurl)
	    
	    req = urllib2.Request(tmpurl)
	    conn = urllib2.urlopen(req, timeout=TIMEOUT_S)
	    conn.read(8) #Try reading a few bytes
	    
	    return tmpurl
	except Exception:
	    print("{0} failed.".format(subkey))
	    print(traceback.format_exc())
	    
	    return None

def processCNTVDefUrl(addon, urlstr):
    pDialog = xbmcgui.DialogProgress()
    pDialog.create(addon.getLocalizedString(30009), addon.getLocalizedString(30010))
    pDialog.update(0)
    try:
        print("Trying CNTVDef Url {0}".format(urlstr))
        
        resp = urllib2.urlopen(urlstr)
        data = resp.read().decode("utf-8")
    
        if pDialog.iscanceled(): return None
    
        url = None
        jsondata = jsonimpl.loads(data)
    
        urlsTried = 0
        urlsToTry = 6 #TODO: dynamic based on the # of elements
    
        if jsondata.has_key("hls_url"):
	    if url == None:
	        urlsTried += 1
	        pDialog.update(urlsTried / urlsToTry * 100, "{0} {1} (HLS)".format(addon.getLocalizedString(30011), "hls1"))
	        url = tryHLSStream(jsondata, "hls1")
	    if url == None:
	        urlsTried += 1
	        pDialog.update(urlsTried / urlsToTry * 100, "{0} {1} (HLS)".format(addon.getLocalizedString(30011), "hls2"))
	        url = tryHLSStream(jsondata, "hls2")
            if url == None:
	        urlsTried += 1
	        pDialog.update(urlsTried / urlsToTry * 100, "{0} {1} (HLS)".format(addon.getLocalizedString(30011), "hls3"))
	        url = tryHLSStream(jsondata, "hls3")
	    if url == None:
	        urlsTried += 1
	        pDialog.update(urlsTried / urlsToTry * 100, "{0} {1} (HLS)".format(addon.getLocalizedString(30011), "hls4"))
	        url = tryHLSStream(jsondata, "hls4")
	    if url == None:
	        urlsTried += 1
	        pDialog.update(urlsTried / urlsToTry * 100, "{0} {1} (HLS)".format(addon.getLocalizedString(30011), "hls5"))
	        url = tryHLSStream(jsondata, "hls5")
	    if url == None:
	        urlsTried += 1
	        pDialog.update(urlsTried / urlsToTry * 100, "{0} {1} (HLS)".format(addon.getLocalizedString(30011), "hls6"))
	        url = tryHLSStream(jsondata, "hls6")
			    
	if pDialog.iscanceled(): return None
	    
	#if url is None and jsondata.has_key("hls_url"):
	#	tryHLSStream(jsondata, "hls4")
	
        if url is None:
	    showNotification(30002)
	    pDialog.close()
	    return None
    
        print("Loading URL {0}".format(url))
        
        auth = urlparse.parse_qs(urlparse.urlparse(url)[4])["AUTH"][0]
        print("Got AUTH {0}".format(auth))
        
        url = url + "|" + urllib.urlencode( { "Cookie" : "AUTH=" + auth } )
        
        print("Built URL {0}".format(url))

        pDialog.close()
        return url
    except Exception:
	showNotification(30000)
	print(traceback.format_exc())
	pDialog.close()
	return None
