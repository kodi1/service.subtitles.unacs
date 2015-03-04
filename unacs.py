# -*- coding: utf-8 -*-

from nsub import log_my, savetofile, list_key
import urllib, urllib2, os
import BaseHTTPServer
import gzip
from StringIO import StringIO
import re
import sys
import imp

from common import *

list = []
values = {'m':'',
          'a':'',
          't':'Submit',
          'g':'',
          'u':'',
          'action':'????',
          'y':'',
          'c':'',
          'l':'0',
          'd':''}

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0 Iceweasel/22.0",
           "Content-type": "application/x-www-form-urlencoded",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Encoding": "gzip, deflate",
           "cache-control":"no-cache",
           "Referer":"http://subsunacs.net/search.php",
           "Host":"subsunacs.net"}

url = 'http://subsunacs.net:80'

def clean_info(dat):
  info = ''
  rex3='&gt;(.*?)&lt;'
  rg = re.compile(rex3, re.IGNORECASE|re.DOTALL)
  a = rg.finditer(dat)
  for m in a:
    info = info + m.group(1)+' '
  return (info.decode('cp1251')).encode('utf-8')

def get_id_url_n(txt, list):
  rex='.*?<td\sclass="tdMovie".*?href="(.*?)\".*?class="tooltip"(.*?)\/div.*?>.*?<\/a><span.*?\((\d+)\).*?<td>(\d)<\/td><td>([0-9.]+)<\/td>.*?"_blank">\s.*?(?:title=")?([0-9.]+)?.><\/a>'
  rg = re.compile(rex, re.IGNORECASE|re.DOTALL)
  a = rg.finditer(txt)
  for m in a:
    rating = m.group(6)
    if None == rating:
      rating = 0
    list.append({'url': m.group(1),
                'info': clean_info(m.group(2)),
                'year': m.group(3),
                'cds': m.group(4),
                'fps': m.group(5),
                'rating': rating,
                'id': __name__})

  return

def get_data(l, key):
  out = []
  for d in l:
    out.append(d[key])
  return out

def read_sub (item):
  log_my(item['title'], item['file_original_path'])

  values['m'] = item['title']
  values['y'] = item['year']

  enc_values = urllib.urlencode(values)
  log_my('Url: ', (url), 'Headers: ', (headers), 'Values: ', (enc_values))

  request = urllib2.Request(url + '/search.php', enc_values, headers)

  response = urllib2.urlopen(request)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])

  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    savetofile(data, __name__+'_tmp.html')
    f.close()
    buf.close()
  else:
    log_my('Error: ', response.info().get('Content-Encoding'))
    return None

  get_id_url_n(data, list)
  for k in list_key:
    d = get_data(list, k)
    log_my(d)
  return list

def get_sub(id, sub_url, filename):
  s = {}
  enc_values = urllib.urlencode(values)
  request = urllib2.Request(url + sub_url, enc_values, headers)
  response = urllib2.urlopen(request)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])
  log_my(response.info())
  s['data'] = response.read()
  s['fname'] = response.info()['Content-Disposition'].split('filename=')[1].strip('"')
  return s
