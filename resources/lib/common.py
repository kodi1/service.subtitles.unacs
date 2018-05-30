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
  import xbmcgui
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

path =''
list_key = ['rating', 'fps', 'url', 'cds', 'info', 'id']

tv_show_list_re = [
                  r'^(?P<tvshow>[\S\s].*?)(?:s)(?P<season>\d{1,2})[_\.\s]?(?:e)(?P<episode>\d{1,2})(?P<title>[\S\s]*)$',
                  r'^(?P<tvshow>[\S\s].*?)(?P<season>\d{1,2})(?P<episode>\d{2})(?P<title>[\S\s]*)$',
                  r'^(?P<tvshow>[\S\s].*?)(?P<season>\d{1,2})(?:x)(?P<episode>\d{1,2})(?P<title>[\S\s]*)$',
                  r'^(?P<season>\d{1,2})(?:x)(?P<episode>\d{1,2})\s(?P<tvshow>[\S\s].*?)$',
                ]

movie_name_re = [
                  r'(\(?(?:19[789]\d|20[01]\d)\)?)',
                  r'(\[\/?B\])',
                  r'(\[\/?COLOR.*?\])',
                  r'\s(X{0,3})(IX|IV|V?I{0,3}):', # Roman numeral followed by a colon
                  r'(\:)',
                  r'(part[\s\S]\d+)'
                ]

search_re =     [
                  (r'(-)', ' '),
                  (r'(\.)', ' '),
                  (r'(\s+)', ' '),
                ]

def log_my(*msg):
  if run_from_xbmc == True:
    xbmc.log((u"*** %s" % (msg,)).encode('utf-8'),level=xbmc.LOGNOTICE)
    #xbmc.log((u"*** %s" % (msg,)).encode('utf-8'),level=xbmc.LOGERROR)
  else:
    for m in msg:
      print m,
    print

def get_search_string (item):
  search_string = item['title']

  if item['mansearch']:
    search_string = item['mansearchstr']
    return search_string

  for name_clean in movie_name_re:
    search_string = re.sub(name_clean, '', search_string)

  if not item['tvshow']:
    for tv_match in tv_show_list_re:
      m = re.match(tv_match, search_string, re.IGNORECASE)
      if m:
        item['tvshow'] = m.group('tvshow')
        item['season'] = m.group('season')
        item['episode']= m.group('episode')
        try: item['title'] = m.group('title') 
        except: pass
        break

  if item['tvshow']:
    if item['season'] and item['episode']:
      search_string = re.sub(r'\s+(.\d{1,2}.*?\d{2}[\s\S]*)$', '', item['tvshow'])
      if int(item['season']) == 0:
        # search for special episodes by episode title
        search_string += ' ' + item['title']
      else: 
        search_string += ' %#02dx%#02d' % (int(item['season']), int(item['episode']))
    else:
      search_string = item['tvshow']

  for f, r in search_re:
    search_string = re.sub(f, r, search_string)

  return search_string

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
