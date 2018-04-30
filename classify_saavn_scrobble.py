#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import collections

SaavnScrobbleFile='/Users/lakshman.narayanan/Downloads/songs-download/saavn/saavnScrobble.txt'
SaavnSortedDir='/Users/lakshman.narayanan/Downloads/songs-download/saavn/'
categoryFile='Categories.txt'

def getCategories(catgyFileName):
    categories = []
    try:
        with open (catgyFileName,'r') as fd:
            for line in fd:
                categories.append(line.strip())
    except FileNotFoundError:
        pass
    return categories

def addCategory(catgyFileName, newCategory, existCategories):
    with open (catgyFileName, 'a') as fd:
        fd.write(newCategory + '\n')
    existCategories.append(newCategory)
    return newCategory

def addSongtoCategory(category, song):
    fileName = os.path.join(SaavnSortedDir, category)
    line = song['title'] + '`' + song['artist'] + '`' + song['album'] + '\n'
    with open (fileName, 'a') as fd:
        fd.write(line)

def buildAllSongsList(categories):
    songsList = collections.defaultdict(dict)
    for cat in categories:
        filename = os.path.join(SaavnSortedDir, cat)
        try:
            with open (filename, 'r') as fd:
                for line in fd:
                    line = line.strip()
                    fields = line.split('`')
                    title = fields[0]
                    artist = fields[1]
                    album = fields[2]
                    if album in songsList:
                        if title in songsList:
                            continue
                        else:
                            songsList[album][title] = cat
                    else:
                        songsList[album][title] = cat
        except FileNotFoundError:
            pass
    return songsList

def askChoice(song, categories):
    print ("What's your category for song:")
    print ("Title:  {}".format(song['title']))
    print ("Album:  {}".format(song['album']))
    print ("Artist: {}".format(song['artist']))
    print ("Available Categories")
    maxN = 0
    for n,cat in enumerate(categories,1):
        print ("{} . {}".format(n,cat))
        maxN = n
    chosen = None
    ok_attempt = 1
    while ok_attempt <= 3:
        try:
            choice = input("Choice:")
            choice = int(choice)
            if choice < 0 or choice > maxN:
                print ("Enter a valid number 0 - {}".format(maxN))
                continue
            chosen = choice
            break;
        except ValueError:
            print ("Enter a number")
    if chosen == None:
        print ("Too many attempts")
        sys.exit(1)
    chosenCategory = ""
    if choice == 0:
        ok_attempt = 1
        while ok_attempt <= 3:
            catName = input ("What's your category name:")
            print ("You chose {}".format(catName))
            ok = input ("yes?")
            if ok == 'yes' or ok == 'y':
                catFile = os.path.join(SaavnSortedDir, categoryFile)
                addCategory(categoryFile, catName, categories)
                chosenCategory = catName
                break;
        if ok_attempt > 3:
            print ("Too many attempts")
            sys.exit(1)
    else:
        chosenCategory = categories[choice-1]
    addSongtoCategory(chosenCategory, song)


def parseScrobbleFile(scrobbleName):
    scrobbledSongs = []
    with open (scrobbleName,'r') as fd:
        for line in fd:
            line = line.strip()
            fields = line.split('`')
            song = {}
            song['title'] = fields[1]
            song['artist'] = fields[2]
            song['album'] = fields[3]
            scrobbledSongs.append(song)
    return scrobbledSongs

def main():
    categories = getCategories(os.path.join(SaavnSortedDir,categoryFile))
    classified_songs = buildAllSongsList(categories)
    scrobbedSongs = parseScrobbleFile(SaavnScrobbleFile)
    for s in scrobbedSongs:
        a = s['album']
        t = s['title']
        if a in classified_songs:
            if t in classified_songs[a]:
                print ("Found {} :{} in {}".format(t,a,classified_songs[a][t]))
                continue
        askChoice(s, categories)


main()


