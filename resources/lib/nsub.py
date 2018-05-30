#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from common import *
import unacs
import subs_sab

def select_1(list):
  l = []
  ls = []
  for lst in list:
    ls.append(os.path.basename(lst))
  dialog = xbmcgui.Dialog()
  n = dialog.select('Select subtitle', ls)
  l.append(list[n])
  return l

def read_sub(*items):
  l = []

  update(os.path.basename(items[0]['file_original_path']),
          'subs_search',
          'title:%(title)s,tvshow:%(tvshow)s,season:%(season)s,episode:%(episode)s' % items[0]
          )

  for item in items:
    search_str = get_search_string(item)
    try:
      ll = unacs.read_sub(search_str, item['year'])
      if ll:
        l.extend(ll)
    except Exception as e:
      log_my('unacs.read_sub', str(e))
      update(os.path.basename(item['file_original_path']),
              'exception',
              'title:%(title)s,tvshow:%(tvshow)s,season:%(season)s,episode:%(episode)s' % item,
              sys.exc_info()
              )

    try:
      ll = subs_sab.read_sub(search_str, item['year'])
      if ll:
        l.extend(ll)
    except Exception as e:
      log_my('subs_sab.read_sub', str(e))
      update(os.path.basename(item['file_original_path']),
              'exception',
              'title:%(title)s,tvshow:%(tvshow)s,season:%(season)s,episode:%(episode)s' % item,
              sys.exc_info()
              )
  if not l:
    return None

  return [i for n,i in enumerate(l) if i not in l[:n]]

def get_sub(id, sub_url, filename):
  r = {}
  if id == 'unacs':
    try:
      r=unacs.get_sub(id, sub_url, filename)
    except:
      update(id, 'exception', sub_url, sys.exc_info())
    else:
      update(r.get('fname','empty'), 'subs_download', sub_url)

  else:
    try:
      r=subs_sab.get_sub(id, sub_url, filename)
    except:
      update(id, 'exception',sub_url, sys.exc_info())
    else:
      update(r.get('fname','empty'), 'subs_download', sub_url)
  return r

def get_dbg_dat(file):
  i = 0
  with open(file, 'rb') as f:
    read = csv.reader(f)
    for row in read:
      i += 1
      if any('title' in s for s in row):
        ret = {}
        ret['num'] = i
        for m in re.finditer(r'(title|tvshow|season|episode):(.*?)(?:,|$)', row[1]):
          ret[m.group(1)] = urllib.unquote_plus(m.group(2))
        yield ret

if __name__ == "__main__":
  cnt = len(sys.argv)
  if cnt == 1:
    sys.exit(1)
  if '-f' == sys.argv[1]:
    import csv
    items = []
    for in_f in [f for f in os.listdir(os.curdir) if f.endswith('.csv')]:
      for r in get_dbg_dat(in_f):
        r['file_original_path'] = ''
        r['year'] = ''
        r['mansearch'] = ''
        items.append(r)
  else:
    items =[{'m':'',
       'title': sys.argv[1],
       'year':'',
       'file_original_path':'',
       'mansearch':'',
       'tvshow':'',
       'season':'',
       'episode':'',
       'num':0,
      }]

  tmp =''
  for item in items:
    if item['tvshow']:
      in_dat = '%(num)d -> T:%(tvshow)s S:%(season)s E:%(episode)s' % item
    else:
      in_dat = '%(num)d -> T:%(title)s' % item
    print in_dat

    l = read_sub(item)
    if l is not None:
      for ll in l:
        tmp = tmp + '%s[%s] %s\n' % ( ll['id'], in_dat, get_info(ll))

    if l and l[-1]['url']:
      log_my(l[-1]['url'])
      r=get_sub(l[-1]['id'], l[-1]['url'], None)
      if (r.has_key('data') and r.has_key('fname')):
        print r['data'][:4]
        savetofile(r['data'], r['fname'])

  savetofile(tmp, 'out.txt')
  sys.exit(0)
