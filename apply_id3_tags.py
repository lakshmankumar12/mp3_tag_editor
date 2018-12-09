#!/usr/bin/python

from __future__ import print_function

import argparse
import subprocess
import os
import sys
import mutagen
import mutagen.id3

parser = argparse.ArgumentParser()
parser.add_argument("-t","--title",  help="title")
parser.add_argument("-a","--artist", help="artist")
parser.add_argument("-l","--album",  help="album")
parser.add_argument("-r","--albumartist",  help="album artist")
parser.add_argument("-R","--albumartistcopy",  help="album artist same as artist", action="store_true")
parser.add_argument("-g","--genre",  help="genre")
parser.add_argument("-y","--year",  help="year")
parser.add_argument("-n","--trackno",  help="track no")
parser.add_argument("-c","--cover",  help="picture")
parser.add_argument("-C","--coverlink",  help="download img from link")
parser.add_argument("--nodv1",      help="dont delete v1")
parser.add_argument("--nodoth",      help="dont delete other tags")
parser.add_argument("file",  help="file")

cmd_options = parser.parse_args()

try:
    new_tag = 0
    existing_tags= mutagen.id3.ID3(cmd_options.file, v2_version=3)
except mutagen.id3._util.ID3NoHeaderError:
    new_tag = 1
    existing_tags= mutagen.id3.ID3()

from mutagen.id3 import TIT2, TALB, TPE1, TPE2, TCON, TYER, TRCK, APIC

good_tags     = [ "TIT2",  "TALB",  "TPE1",   "TPE2",        "TCON",  "TYER", "TRCK",  ]
good_tags_ctr = [ TIT2,    TALB,    TPE1,     TPE2,          TCON,    TYER,   TRCK  ]
args          = [ "title", "album", "artist", "albumartist", "genre", "year", "trackno"]

if cmd_options.albumartistcopy:
    setattr(cmd_options,"albumartist", cmd_options.artist)

new_tags = {}
for tag,arg,ctr in zip(good_tags,args,good_tags_ctr):
    value_to_assign = None
    current_value = None
    if hasattr(cmd_options, arg):
        value_to_assign = getattr(cmd_options, arg)
    if tag in existing_tags:
        current_value = existing_tags[tag]
    if value_to_assign:
        new_tags[tag] = ctr(encoding=3, text=[value_to_assign])
    elif current_value:
        new_tags[tag] = current_value

if cmd_options.cover:
    if cmd_options.cover.upper().endswith("JPG") or cmd_options.cover.upper().endswith("JPEG"):
        with open (cmd_options.cover,"rb") as fd:
            new_tags["APIC"] = APIC(encoding=3, mime='image/jpeg', type=3,
                                    desc=u'Front Cover', data=fd.read())
elif cmd_options.coverlink:
    print("Downloading cover")
    cmd=["curl",cmd_options.coverlink,"-o","cover.jpg"]
    cmd_str=" ".join(cmd)
    print ("Executing:%s"%cmd_str)
    subprocess.check_output(cmd)
    with open ("cover.jpg","rb") as fd:
        new_tags["APIC"] = APIC(encoding=3, mime='image/jpeg', type=3,
                                desc='Front Cover', data=fd.read())
elif u"APIC:" in existing_tags:
    new_tags[u"APIC:"] = existing_tags[u"APIC:"]

if not new_tag:
    existing_tags.delete()
    existing_tags.save(v2_version=3)

for k in new_tags:
    existing_tags[k] = new_tags[k]
if new_tag:
    existing_tags.save(cmd_options.file, v2_version=3)
else:
    existing_tags.save(v2_version=3)

