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

def read_sub (item):
  update(os.path.basename(item['file_original_path']),
          'subs_search',
          'title:%(title)s,tvshow:%(tvshow)s,season:%(season)s,episode:%(episode)s' % item
          )
  l = []
  ret = 0
  try:
    l.extend(unacs.read_sub(item))
  except Exception as e:
    log_my('unacs.read_sub', str(e))
    update(os.path.basename(item['file_original_path']),
            'exception',
            'title:%(title)s,tvshow:%(tvshow)s,season:%(season)s,episode:%(episode)s' % item,
            sys.exc_info()
            )
    ret += 1
  try:
    l.extend(subs_sab.read_sub(item))
  except Exception as e:
    log_my('subs_sab.read_sub', str(e))
    update(os.path.basename(item['file_original_path']),
            'exception',
            'title:%(title)s,tvshow:%(tvshow)s,season:%(season)s,episode:%(episode)s' % item,
            sys.exc_info()
            )
    ret += 2
  if ret == 3: return None
  return l

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

if __name__ == "__main__":
  cnt = len(sys.argv)
  item ={'m':'',
         'title':'',
         'year':'',
         'file_original_path':'',
         'mansearch':'',
         'tvshow':'',
         'season':'',
         'episode':'',
        }

  if cnt == 3:
    item['year'] = sys.argv[2]
  elif cnt == 1:
    sys.exit(1)
  item['title'] = sys.argv[1]

  l = unacs.read_sub(item)
  l += subs_sab.read_sub(item)

  tmp =''
  for ll in l:
    tmp = tmp + get_info(ll)+'>>>>'+'\n'

  savetofile(tmp, 'out.txt')

  log_my(l[-1]['url'])

  if l[-1]['id'] == 'unacs':
    r=unacs.get_sub(None, l[-1]['url'], None)
  else:
    r=subs_sab.get_sub(None, l[-1]['url'], None)
  if (r.has_key('data') and r.has_key('fname')):
    print r['data'][:4]
    savetofile(r['data'], r['fname'])
  sys.exit(0)