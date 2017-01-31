# -*- coding: utf-8 -*-
import sys
import urlparse
import urllib2
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import xml.dom.minidom
from resources.lib.cntvresolver import processCNTVDefUrl

addon = xbmcaddon.Addon(id="plugin.video.mytv")
plugin_url = sys.argv[0]
handle = int(sys.argv[1])
params = dict(urlparse.parse_qsl(sys.argv[2].lstrip('?')))
cntv = "vdn.live.cntv.cn/api2/live.do"

def get_dom():
    return xml.dom.minidom.parse(
            urllib2.urlopen(addon.getSetting("listUrl")))

def find_element(dom, tag, attr_name, attr_val):
    return [e for e in dom.getElementsByTagName(tag)
                if e.getAttribute(attr_name) == attr_val][0]

def index():
    for node in get_dom().getElementsByTagName('class'):
        li = xbmcgui.ListItem(node.getAttribute('classname'))
        url = plugin_url + '?act=channel&id=' + node.getAttribute('id')

        xbmcplugin.addDirectoryItem(handle, url, li, True)

    xbmcplugin.endOfDirectory(handle)

def get_final_url(url):
    try:
	urlRequest = urllib2.urlopen(url, timeout = 1)
        resolvedUrl = urlRequest.geturl()
        print("url resolved to: {0}".format(resolvedUrl))
        return resolvedUrl
    except Exception as e:
        print str(e)
	return url
    
def get_redirect(tvlink):
    try:
        redirect = tvlink.getAttribute('redirect')
        print ("Redirect flag is {0}".format(redirect))
	return redirect
    except Exception:
	return 'false'
		
def list_channel():
    class_node = find_element(get_dom(), 'class', 'id', params['id'])
    for channel in class_node.getElementsByTagName('channel'):
        titleOfChannel = channel.getAttribute('name')
        tvlinks = channel.getElementsByTagName('tvlink')
        if not tvlinks: #if no tvlink presents, skip
            continue

        li = xbmcgui.ListItem(titleOfChannel)
        if len(tvlinks) == 1: #play directly if only has one tvlink
            url = tvlinks[0].getAttribute('link')
	    if get_redirect(tvlinks[0]) == 'true':
		url =get_final_url(url)
            # determine if we need to process with the CNTV approach
            if cntv in url:
                url = plugin_url + '?act=cnresolve&title='+titleOfChannel+'&url='+url
            else:
                # find the final url
                #url = get_final_url(url)
                li.setProperty('mimetype', 'video/x-msvideo') #prevent getting mime type
                li.setProperty('IsPlayable', 'true') #required by setResolvedUrl
                # update the title instead of the filename
                li.setInfo('video', {'Title': titleOfChannel})
        else:
            url = plugin_url + '?act=choice&id=' + channel.getAttribute('id')

        xbmcplugin.addDirectoryItem(handle, url, li)

    xbmcplugin.endOfDirectory(handle)

def choice_tvlink():
    node = find_element(get_dom(), 'channel', 'id', params['id'])
    titleOfChannel = node.getAttribute('name')
    tvlinks = [(tvlink.getAttribute('source'), tvlink.getAttribute('link'), get_redirect(tvlink))
                    for tvlink in node.getElementsByTagName('tvlink')]
    choice = xbmcgui.Dialog().select('选择信号源', [s[0] for s in tvlinks])
    li = xbmcgui.ListItem(titleOfChannel, path=tvlinks[choice][1])
    #xbmcplugin.setResolvedUrl(handle, True, li)
    sourceUrl = tvlinks[choice][1]
	
    if tvlinks[choice][2] == 'true':
	sourceUrl =get_final_url(sourceUrl)

    if cntv in sourceUrl:
        sourceUrl = processCNTVDefUrl(addon, sourceUrl)
    # update the title instead of the filename
    li.setInfo('video', {'Title': titleOfChannel})
    # find the final url
    #sourceUrl = get_final_url(sourceUrl)
    xbmc.Player().play(sourceUrl, li)

def resolve_cntv():
    cnurl = params['url']
    titleOfChannel = params['title']
    cnurl = processCNTVDefUrl(addon, cnurl)
    if cnurl == None:
        return
    li = xbmcgui.ListItem(titleOfChannel)
    li.setInfo('video', {'Title': titleOfChannel})
    # find the final url
    #cnurl = get_final_url(cnurl)
    xbmc.Player().play(cnurl,li)
    
    
{
    'index': index,
    'channel': list_channel,
    'choice': choice_tvlink,
    'cnresolve': resolve_cntv,
}[params.get('act', 'index')]()
