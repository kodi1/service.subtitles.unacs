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
  l = []
  ret = 0
  try:
    l.extend(unacs.read_sub(item))
  except Exception as e:
    log_my('unacs.read_sub', str(e))
    ret += 1
  try:
    l.extend(subs_sab.read_sub(item))
  except Exception as e:
    log_my('subs_sab.read_sub', str(e))
    ret += 2
  if ret == 3: return None
  return l

def get_sub(id, sub_url, filename):
  if id == 'unacs':
    r=unacs.get_sub(id, sub_url, filename)
  else:
    r=subs_sab.get_sub(id, sub_url, filename)
  return r

if __name__ == "__main__":
  cnt = len(sys.argv)
  item ={'m':'',
         'title':'',
         'year':'',
         'file_original_path':''
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