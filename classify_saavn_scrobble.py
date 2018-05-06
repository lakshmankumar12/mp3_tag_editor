#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import collections
import argparse

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
    total_cnt = 0
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
                        if title in songsList[album]:
                            continue
                        else:
                            songsList[album][title] = cat
                            total_cnt += 1
                    else:
                        songsList[album][title] = cat
                        total_cnt += 1
        except FileNotFoundError:
            pass
    return (songsList, total_cnt)

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
                addCategory(catFile, catName, categories)
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

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="print parsed files too", action="store_true")

    cmd_options = parser.parse_args()

    categories = getCategories(os.path.join(SaavnSortedDir,categoryFile))
    classified_songs, total_cnt = buildAllSongsList(categories)
    scrobbedSongs = parseScrobbleFile(SaavnScrobbleFile)
    new_count = 0
    for s in scrobbedSongs:
        a = s['album']
        t = s['title']
        if a in classified_songs:
            if t in classified_songs[a]:
                if cmd_options.debug:
                    print ("Found {} :{} in {}".format(t,a,classified_songs[a][t]))
                continue
        askChoice(s, categories)
        new_count += 1
    print ("There were {} classfied songs and now you classified {} songs".format(total_cnt, new_count))


main()


