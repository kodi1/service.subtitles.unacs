#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, sys, os
import BaseHTTPServer
import gzip
from StringIO import StringIO
import re
import sys
import imp

try:
    import xbmc
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
list = []
list_key = ['rating', 'fps', 'url', 'cds', 'info']
values = {'m':'',
          'f':'????',
          'a':'',
          't':'Submit',
          'g':'',
          'u':'',
          'action':'',
          'y':'',
          'c':'',
          'l':'-1',}

headers = {"Uer-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0 Iceweasel/22.0",
           "Content-type": "application/x-www-form-urlencoded",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Encoding": "gzip, deflate",
           "cache-control":"no-cache"}

url = 'http://subsunacs.net:80'

def log_my(*msg):
  if run_from_xbmc == True:
    xbmc.log((u"### SSS-> %s" % (msg,)).encode('utf-8'),level=xbmc.LOGNOTICE)
    #xbmc.log((u"### SSS-> %s" % (msg,)).encode('utf-8'),level=xbmc.LOGERROR)
  else:
    for m in msg:
      print m,
    print

def get_info(it):
  str = 'Fps:{0} Cd:{1} - {2}'.format(it['fps'], it['cds'], it['info'])
  return str

def savetofile(d, name):
  if run_from_xbmc == False:
    n = os.path.join(path, name)
    f = open(n, 'wb')
    f.write(d)
    f.close

def clean_info(dat):
  info = ''
  rex3='&gt;(.*?)&lt;'
  rg = re.compile(rex3, re.IGNORECASE|re.DOTALL)
  a = rg.finditer(dat)
  for m in a:
    info = info + m.group(1)+' '
  return (info.decode('cp1251')).encode('utf-8')

def get_id_url_n(txt, list):
  rex1='.*?<tr .*?"tdMovie".*?get\.php\?id=(\d+).*?class="tooltip"'
  rex2='(.*?)/div'
  rex3='.*?>(.*?)</a><span.*?\((\d{4})\)</span>.*?</td><td>(\d{1})</td><td>([0-9.]+)</td><td><a\s+href="rating.php\?id=\d+.*?((?<=title=")[0-9.]+)?.></a></td>.*?</tr>'
  rg = re.compile(rex1+rex2+rex3, re.IGNORECASE|re.DOTALL)
  a = rg.finditer(txt)
  for m in a:
    rating = m.group(7)
    if None == rating:
      rating = 0
    list.append({'url': m.group(1),
                'info': clean_info(m.group(2)),
                'year': m.group(4),
                'cds': m.group(5),
                'fps': m.group(6),
                'rating': rating})

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
    savetofile(data, 'tmp.html')
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
  request = urllib2.Request(url + '/get.php?id=' + sub_url, enc_values, headers)
  response = urllib2.urlopen(request)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])
  log_my(response.info())
  s['data'] = response.read()
  s['fname'] = response.info()['Content-Disposition'].split('filename=')[1].strip('"')
  return s

def select_1(list):
  l = []
  ls = []
  for lst in list:
    ls.append(os.path.basename(lst))
  dialog = xbmcgui.Dialog()
  n = dialog.select('Select subtitle', ls)
  l.append(list[n])
  return l

if __name__ == "__main__":
  cnt = len(sys.argv)
  item ={'m':'',
         'title':'',
         'year':'',
         'file_original_path':''
        }

  if cnt == 2:
    item['title'] = sys.argv[1]
  elif cnt == 3:
    item['year'] = sys.argv[2]
  elif cnt == 1:
    item['title'] = 'gravity'
    #sys.exit(1)

  l = read_sub(item)
  tmp =''
  for ll in l:
    tmp = tmp + get_info(ll)+'>>>>'+'\n'

  savetofile(tmp, 'topki.txt')

  log_my(l[-1]['url'])
  r=get_sub(None, l[-1]['url'], None)
  if (r.has_key('data') and r.has_key('fname')):
    print r['data'][:4]
    savetofile(r['data'], r['fname'])
  sys.exit(0)