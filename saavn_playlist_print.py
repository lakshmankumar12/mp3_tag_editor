#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
We assume there is a /tmp/a.html that contains a playlist in display
This just prints the songs from that playlist.
'''

import bs4
import sys
import json
from html import unescape

souped = None
with open ('/tmp/a.html','r') as fd:
    souped = bs4.BeautifulSoup(fd.read(), 'html.parser')

trackList = souped.find("ol", {"class": "track-list"})
if not trackList:
    print("Couldn't spot track-list from the page")
    sys.exit(1)
trackList = trackList

li_items = trackList.findAll('li', recursive=False)
tracks = []
titmaxwidth = 10
albmaxwidth = 10
for li in li_items:
    songJsonStr = li.find('div', {"class": "song-json"})
    if not songJsonStr:
        print ("Couldn't spot song-json in list-item")
        sys.exit(1)
    songJsonStr = songJsonStr.get_text()
    songInfo = json.loads(songJsonStr)
    title = unescape(songInfo['title'])
    album = unescape(songInfo['album'])
    year = unescape(songInfo['year'])
    titmaxwidth = max(titmaxwidth, len(title))
    albmaxwidth = max(albmaxwidth, len(album))
    tracks.append((title,album,year))

for n,(t,a,y) in enumerate(tracks,1):
    print (" {:3} . {:{titwidth}}  | {:{albwidth}} | {}".format(n, t, a, y, titwidth=titmaxwidth, albwidth=albmaxwidth))

