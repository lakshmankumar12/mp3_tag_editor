#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This prints the songs in a current play-list displayed in saavn page.
'''

import bs4
import sys
import json
from html import unescape
import argparse

sys.path.append('/Users/lakshman.narayanan/github/mac_scripts')
import mac_script_helper
from colorama import Fore, Back, Style

def getSaavnPage():
    js = [
          mac_script_helper.SaveDocCmd,
         ]
    bwsrTab = mac_script_helper.BrowserTab('https://www.jiosaavn.com')
    err,page,_ = bwsrTab.sendCommands(js)
    if err != 0:
        print ("Trouble in getting page-info from saavn")
        sys.exit(1)

    if len (page.strip()) == 0:
        sys.exit(1)

    souped = bs4.BeautifulSoup(page, 'html.parser')
    with open ('/tmp/a.html','w') as fd:
        fd.write(souped.prettify())

    return souped

def getSongsList(souped):
    trackList = souped.find("ol", {"class": "track-list"})
    if not trackList:
        print("Couldn't spot track-list from the page")
        sys.exit(1)
    trackList = trackList

    li_items = trackList.findAll('li', recursive=False)
    tracks = []
    titmaxwidth = 10
    albmaxwidth = 10
    artmaxwidth = 10
    for li in li_items:
        songJsonStr = li.find('div', {"class": "song-json"})
        if not songJsonStr:
            print ("Couldn't spot song-json in list-item")
            sys.exit(1)
        songJsonStr = songJsonStr.get_text()
        songInfo = json.loads(songJsonStr)
        title = unescape(songInfo['title'])
        artist = unescape(songInfo['singers'])
        album = unescape(songInfo['album'])
        year = unescape(songInfo['year'])
        link = unescape(songInfo['perma_url'])
        titmaxwidth = max(titmaxwidth, len(title))
        artmaxwidth = max(artmaxwidth, len(artist))
        albmaxwidth = max(albmaxwidth, len(album))
        tracks.append((title,artist,album,year,link))

    return ((titmaxwidth, artmaxwidth, albmaxwidth), tracks)

def printScreenFriendly(maxwidths, tracks):
    (tw, rw, aw) = maxwidths

    for n,(t,r,a,y,l) in enumerate(tracks,1):
        print (" {:3} . {:{titwidth}} | {:{artwidth}} | {:{albwidth}} | {} | {}".format(n, t, r, a, y, l, titwidth=tw, artwidth=rw, albwidth=aw))

def dumpTracksInFile(tracks, filename):
    with open(filename, 'w') as fd:
        for t,r,a,y,l in tracks:
            print ('{}`{}`{}`{}'.format(t,r,a,l), file=fd)

def main():
    souped = getSaavnPage()

    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--file", help="write to file", default="/tmp/saavn-playlist")
    parser.add_argument("-s","--screen", help="write to screen", action="store_true")
    cmd_options = parser.parse_args()

    widths, tracks = getSongsList(souped)

    if cmd_options.file:
        dumpTracksInFile(tracks, cmd_options.file)

    if cmd_options.screen:
        printScreenFriendly(widths, tracks)

if __name__ == "__main__":
    main()

