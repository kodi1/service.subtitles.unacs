# -*- coding: utf-8 -*-

import urllib, urllib2, os
import BaseHTTPServer
import gzip
from StringIO import StringIO
import re
import sys
import imp
from httplib import *

from common import *

list = []

values = {'movie':'',
          'act':'search',
          'select-language':'2',
          'upldr':'',
          'yr':'',
          'release':''}

head = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0 Iceweasel/22.0",
           "Content-type": "application/x-www-form-urlencoded",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Encoding": "gzip, deflate",
           "Referer":"http://subs.sab.bz/index.php?",
           "Host":"subs.sab.bz",
           "Accept-Language":"en-US,en;q=0.5"
           }

url = "subs.sab.bz"

def clean_info(dat):
  info = ''
  rex3='&gt;(.*?)&lt;'
  rg = re.compile(rex3, re.IGNORECASE|re.DOTALL)
  a = rg.finditer(dat)

  for m in a:
    info = info + m.group(1)+' '
  return (info.decode('cp1251')).encode('utf-8')

def get_id_url_n(txt, list):
  rex='[\s\S]*?<tr[\s\S]class="subs-row">[\s\S]*?<td[\s\S]class="c2field"><a[\s\S]href="[\s\S]*?download&attach_id=(\d+)"[\s\S]*?onmouseover[\s\S]*?target=[\s\S](.*?)onmouseout=[\s\S]*?<\/a>\s\((\d+)\)[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?<td>(\d)[\s\S]*?<td>([0-9.]+)[\s\S]*?title="rating:\s(\d)[\s\S]*?<\/tr>'
  rg = re.compile(rex, re.IGNORECASE|re.DOTALL)
  a = rg.finditer(txt)

  for m in a:
    list.append({'url': m.group(1),
                'info': clean_info(m.group(2)),
                'year': m.group(3),
                'cds': m.group(4),
                'fps': m.group(5),
                'rating': m.group(6),
                'id': __name__})

  return

def get_data(l, key):
  out = []
  for d in l:
    out.append(d[key])
  return out

def read_sub (item):
  log_my(item['title'], item['file_original_path'])

  values['movie'] = item['title']
  values['yr'] = item['year']

  enc_values = urllib.urlencode(values)
  log_my('Url: ', (url), 'Headers: ', (head), 'Values: ', (enc_values))

  connection = HTTPConnection(url)
  connection.request("POST", "/index.php?", headers=head, body=enc_values)
  response = connection.getresponse()

  log_my(response.status, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.status][0])

  if response.status == 200 and response.getheader('content-type').split(';')[0] == 'text/html':
    log_my(response.getheaders())
    data = response.read()
    savetofile(data, __name__+'_tmp.html')
  else:
    connection.close()
    return None

  connection.close()
  get_id_url_n(data, list)
  for k in list_key:
    d = get_data(list, k)
    log_my(d)
  return list

def get_sub(id, sub_url, filename):
  s = {}
  connection = HTTPConnection(url)
  connection.request("GET", "/index.php?act=download&attach_id="+sub_url, headers=head)
  response = connection.getresponse()

  log_my(response.status, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.status][0])
  log_my(response.getheaders())

  if response.status != 200:
    connection.close()
    return None

  s['data'] = response.read()
  s['fname'] = response.getheader('Content-Disposition').split('filename=')[1].strip('"')
  connection.close()
  return s
