# -*- coding: utf-8 -*-

from nsub import log_my, savetofile, list_key
from common import *

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

headers = {
            "Host": "subsunacs.net",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
          }

url = 'https://subsunacs.net'
clean_str = r"(<div.*?>|<\/div>|<span.*?>|<\/span>|<img.*?>|<a[\s\S]*?>|<\/a>|<\/?b>|<br\s?\/>|<br>|\&\S*?;|<\/?u>|<\/?strong>|<\/?em>)"

def get_id_url_n(txt, list):
  soup = BeautifulSoup(txt, 'html5lib')
  # dump_src(soup, 'src.html')
  for link in soup.find_all('a', href=re.compile(r'(?:\/subtitles\/\w+.*\/$)')):
    t = link.find_parent('td').find_next_siblings('td')

    y = link.find_next_sibling('span', text=True)
    if y:
      yr = y.get_text().split('(')[1].split(')')[0]
    else:
      yr = 'n/s'

    list.append({'url': link['href'],
              'info': re.sub(clean_str, " ", link.get('title').encode('utf-8', 'replace')),
              'year': yr,
              'cds': t[0].string.encode('utf-8', 'replace'),
              'fps': t[1].string.encode('utf-8', 'replace'),
              'rating': t[2].a.img and t[2].a.img.get('alt') or '0.0',
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

  values['m'] = mov
  values['y'] = year

  enc_values = urllib.urlencode(values)
  log_my('Url: ', (url), 'Headers: ', (headers), 'Values: ', (enc_values))

  request = urllib2.Request(url + '/search.php', enc_values, headers)

  response = urllib2.urlopen(request)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])

  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    f.close()
    buf.close()
  else:
    log_my('Error: ', response.info().get('Content-Encoding'))
    return None

  get_id_url_n(data, list)
  if run_from_xbmc == False:
    for k in list_key:
      d = get_data(list, k)
      log_my(d)

  return list

def get_sub(id, sub_url, filename):
  s = {}
  enc_values = urllib.urlencode(values)
  headers['Referer'] = url + '/search.php?'
  request = urllib2.Request(url + sub_url, enc_values, headers)
  response = urllib2.urlopen(request)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])
  s['data'] = response.read()
  s['fname'] = response.info()['Content-Disposition'].split('filename=')[1].strip('"')
  return s
