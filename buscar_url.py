import urllib.request
import ssl
import sqlite3
from bs4 import BeautifulSoup
import random
from urllib.parse import urlparse
from urllib.parse import urljoin


contx = ssl.create_default_context()
contx.check_hostname = False
contx.verify_mode = ssl.CERT_NONE

conectar = sqlite3.connect('buscador.db')
curs = conectar.cursor()

curs.execute('''
CREATE TABLE IF NOT EXISTS Busquedas(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
url TEXT UNIQUE,
error INTEGER,
html TEXT
)
''')


urlset = list()
count = int(input('How many pages would you like to retrieve?: '))

while True:
    if len(urlset) < 1:
        url = input('Ingrese una url: type d for default url: ')
        if len(url) < 1: break
        if url == 'd': url = 'https://www.google.com/'

    else:
        url = random.choice(urlset)
        urlset.remove(url)
    if url.endswith('/'): url = url[:-1]

    try:
        abrir = urllib.request.urlopen(url, context=contx)
        html = abrir.read()
        if abrir.getcode() == 200:
            curs.execute('INSERT OR IGNORE INTO Busquedas(url, error) VALUES(?,?)', (url, abrir.getcode()))
        else:
            curs.execute('INSERT INTO Busquedas(url, error) VALUES(?,?,?)', (url, abrir.getcode()))
            continue

        if abrir.info().get_content_type() != 'text/html':
            curs.execute('UPDATE Busquedas SET html=? WHERE url=?', ('empty', url))
            continue
        else:
            curs.execute('UPDATE Busquedas SET html=? WHERE url=?', (html, url))
        conectar.commit()

        soup = BeautifulSoup(html, 'html.parser')

    except:
        print('No se pudo abrir la url', url)
        continue

    urlset.clear()
    tags = soup('a')

    for tag in tags:
        href = tag.get('href', None)
        if href is None: continue
        fi = href.find('#')
        href = href[:fi]
        check = urlparse(href)
        if len(check.scheme) < 1:
            href = urljoin(url, href)
        if href.endswith('.png') or href.endswith('jpg') or href.endswith('gif'): continue
        if href.endswith('/'): href = href[:-1]
        urlset.append(href)
    count -= 1
    conectar.commit()
    if count < 1: break
