# -*- coding: utf-8 -*-

from nsub import log_my, savetofile, list_key
from common import *

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
clean_str = r"(ddri\S*?'|','\#\S+\)|<div.*?>|<\/div>|<span.*?>|<\/span>|<img.*?\/>|<a[\s\S]*?>|<\/a>|<\/?b>|<br\s?\/>|&lt;b&gt;|\&\S*?;|\/[ab]|br\s\/|a\shref.*?_blank)|<\/?i>|<\/?font.*?>"
def get_id_url_n(txt, list):
  soup = BeautifulSoup(txt, 'html5lib')
  for link in soup.find_all('a', href=re.compile(r'[\S]attach_id=(?:\d+)')):
    p = link.find_parent('td')
    t = p.find_next_siblings('td', text=True)

    y = p.get_text()
    if y:
      yr = y.split('(')[1].split(')')[0]
    else:
      yr = 'n/s'

    list.append({'url': link['href'].split('attach_id=')[1],
                'info': re.sub(clean_str, " ", link.get('onmouseover').encode('utf-8', 'replace')),
                'year': yr,
                'cds': t[2].string.encode('utf-8', 'replace'),
                'fps': t[3].string.encode('utf-8', 'replace'),
                'rating': link.find_parent('tr').find(href='#').img.get('alt').split(':')[1].strip(),
                'id': __name__})

  return

def get_data(l, key):
  out = []
  for d in l:
    out.append(d[key])
  return out

def read_sub (mov, year):
  list = []
  log_my(mov, year)

  values['movie'] = mov
  values['yr'] = year

  enc_values = urllib.urlencode(values)
  log_my('Url: ', (url), 'Headers: ', (head), 'Values: ', (enc_values))

  connection = HTTPConnection(url)
  connection.request("POST", "/index.php?", headers=head, body=enc_values)
  response = connection.getresponse()

  log_my(response.status, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.status][0])

  if response.status == 200 and response.getheader('content-type').split(';')[0] == 'text/html':
    log_my(response.getheaders())
    data = response.read()
  else:
    connection.close()
    return None

  connection.close()

  get_id_url_n(data, list)
  if run_from_xbmc == False:
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
