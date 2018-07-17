#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Print's current saavn playing page's playqueue.
'''

import bs4
import sys
sys.path.append('/Users/lakshman.narayanan/github/mac_scripts')
import mac_script_helper
from colorama import Fore, Back, Style

js = [
      mac_script_helper.SaveDocCmd,
     ]
bwsrTab = mac_script_helper.BrowserTab('https://www.saavn.com')
err,page,_ = bwsrTab.sendCommands(js)
if err != 0:
    print ("Trouble in getting page-info from saavn")
    sys.exit(1)

if len (page.strip()) == 0:
    sys.exit(1)

souped = bs4.BeautifulSoup(page, 'html.parser')
with open ('/tmp/a.html','w') as fd:
    fd.write(souped.prettify())

drawer = souped.find("ol", {"id": "drawer-queue-group"})
if not drawer:
    print("Couldn't spot drawer-scroll from the page")
    sys.exit(1)

li_items = drawer.findAll('li', recursive=False)
tracks = []
maxwidth = 10
for li in li_items:
    title = li.find('h4')
    album = li.find('h5')
    if not title or not album:
        print ("Couldn't spot h4/h5 tag in list-item")
        sys.exit(1)
    playing = False
    if 'class' in li.attrs:
        if 'now-playing' in li.attrs['class']:
            playing=True
    t = title.get_text().strip()
    maxwidth = max(maxwidth, len(t))
    a = album.get_text().strip()
    tracks.append((t,a,playing))

for n,(t,a,p) in enumerate(tracks,1):
    if p:
        st="*"
        style = Fore.RED
    else:
        st=" "
        style = ""
    print (style + " {:3}{:1} . {:{width}}  | {} ".format(n, st, t, a, width=maxwidth) + Style.RESET_ALL)

