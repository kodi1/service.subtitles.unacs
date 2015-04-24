# -*- coding: utf-8 -*-

import sys
import os
from bs4 import BeautifulSoup

import urllib, urllib2, os
import BaseHTTPServer
import gzip
from StringIO import StringIO
import re
import imp
from httplib import *

try:
  import xbmc
  from ga import ga
  run_from_xbmc = True
except ImportError:
  run_from_xbmc = False
  pass

if run_from_xbmc == True:
  import xbmcvfs
  import xbmcaddon
  import xbmcgui
  import xbmcplugin

list_key = ['rating', 'fps', 'url', 'cds', 'info', 'id']
path =''

def log_my(*msg):
  if run_from_xbmc == True:
    xbmc.log((u"*** %s" % (msg,)).encode('utf-8'),level=xbmc.LOGNOTICE)
    #xbmc.log((u"*** %s" % (msg,)).encode('utf-8'),level=xbmc.LOGERROR)
  else:
    for m in msg:
      print m,
    print

def update(name, act_ev, dat, crash=None):
  payload = {}
  payload['ec'] = name
  payload['ea'] = act_ev
  payload['ev'] = '1'
  payload['dl'] = urllib.quote_plus(dat.encode('utf-8'))
  if run_from_xbmc == True:
    payload['an'] = xbmcaddon.Addon().getAddonInfo('name')
    payload['av'] = xbmcaddon.Addon().getAddonInfo('version')
    ga().update(payload, crash)
  else:
    print payload

def get_info(it):
  str = 'Fps:{0} Cd:{1} - {2}'.format(it['fps'], it['cds'], it['info'])
  return re.sub("  ", " ", str)

def savetofile(d, name):
  if run_from_xbmc == False:
    n = os.path.join(path, name)
    f = open(n, 'wb')
    f.write(d)
    f.close

def dump_src(s, name):
  if run_from_xbmc == False:
    f = open(name,'wb')
    f.write(s.prettify().encode('utf-8', 'replace'))
    f.close()
