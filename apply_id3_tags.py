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
parser.add_argument("-g","--genre",  help="genre")
parser.add_argument("-y","--year",  help="year")
parser.add_argument("-n","--trackno",  help="track no")
parser.add_argument("-c","--cover",  help="picture")
parser.add_argument("--nodv1",      help="dont delete v1")
parser.add_argument("--nodoth",      help="dont delete other tags")
parser.add_argument("file",  help="file")

parsed_args = parser.parse_args()

existing_tags= mutagen.id3.ID3(parsed_args.file, v2_version=3)

from mutagen.id3 import TIT2, TALB, TPE1, TPE2, TCON, TYER, TRCK, APIC

good_tags     = [ "TIT2",  "TALB",  "TPE1",   "TPE2",        "TCON",  "TYER", "TRCK",  ]
good_tags_ctr = [ TIT2,    TALB,    TPE1,     TPE2,          TCON,    TYER,   TRCK  ]
args          = [ "title", "album", "artist", "albumartist", "genre", "year", "trackno"]

new_tags = {}
for tag,arg,ctr in zip(good_tags,args,good_tags_ctr):
    value_to_assign = None
    current_value = None
    if hasattr(parsed_args, arg):
        value_to_assign = getattr(parsed_args, arg)
    if tag in existing_tags:
        current_value = existing_tags[tag]
    if value_to_assign:
        new_tags[tag] = ctr(text=[value_to_assign])
    elif current_value:
        new_tags[tag] = current_value

if "APIC" in existing_tags:
    new_tags["APIC"] = existing_tags["APIC"]
elif parsed_args.cover:
    if parsed_args.cover.upper().endswith("JPG") or parsed_args.cover.upper().endswith("JPEG"):
        with open (parsed_args.cover,"r") as fd:
            new_tags["APIC"] = APIC(encoding=3, mime='image/jpeg', type=3,
                                    desc=u'Front Cover', data=fd.read())
existing_tags.delete()
existing_tags.save(v2_version=3)

for k in new_tags:
    existing_tags[k] = new_tags[k]
existing_tags.save(v2_version=3)

