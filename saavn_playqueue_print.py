#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
We assume there is a /tmp/a.html that contains current saavn playing page.
This just prints the current play queue from that!
'''

import bs4
import sys
import pdb

souped = None
with open ('/tmp/a.html','r') as fd:
    souped = bs4.BeautifulSoup(fd.read(), 'html.parser')

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
    else:
        st=" "
    print (" {:3}{:1} . {:{width}}  | {} ".format(n, st, t, a, width=maxwidth))

