#!/usr/bin/python

'''
  This can strip the start and end seconds from one file to another.

  It uses avconv for that. avconv does preserve album art but leaves
  all other tags empty! So, this can copy the tags from src to dest.
  You can also use this just to copy tags
'''

from __future__ import print_function

import argparse
import subprocess
import os
import sys
import mutagen
import mutagen.id3

parser = argparse.ArgumentParser()
parser.add_argument("-u","--update",   help="update same file. dest arg is ignored", action="store_true")
parser.add_argument("--cptag",   help="just copy tags from one file to antoher", action="store_true")
parser.add_argument("--ss",  help="start time")
parser.add_argument("--to",  help="end time")
parser.add_argument("src",   help="src file")
parser.add_argument("dest",  help="dest file", nargs='?')

parsed_args = parser.parse_args()

if parsed_args.update:
    if parsed_args.dest:
        print("You can specify both --update and destination file")
        sys.exit(1)
    (filename,extension) = os.path.splitext(parsed_args.src)
    parsed_args.dest=filename+'-new'+extension
elif not parsed_args.dest:
    print ("You should either specify --update or a dest file")
    sys.exit(1)

if parsed_args.cptag and parsed_args.update:
    print ("If --cptag is given an explicit existing destionation should be given")
    sys.exit(1)

if parsed_args.cptag:
    if not os.path.exists(parsed_args.dest):
        print ("'%s' doesn't already exist."%parsed_args.dest)
        sys.exit(1)
    if parsed_args.ss or parsed_args.to:
        print ("when --cptag we dont update time. If you want to update time, tags are automatically cp'ed into the new file")
        sys.exit(1)
else:
    if os.path.exists(parsed_args.dest):
        print ("'%s' already exists. rm it first"%parsed_args.dest)
        sys.exit(1)

if parsed_args.ss or parsed_args.to:
    if "'" in parsed_args.src:
        s = '"%s"'%parsed_args.src
        d = '"%s"'%parsed_args.dest
    else:
        s = "'%s'"%parsed_args.src
        d = "'%s'"%parsed_args.dest
    cmd="avconv -i %s -acodec copy -vn "%s
    if parsed_args.ss:
        cmd+='-ss %s '%parsed_args.ss
    if parsed_args.to:
        cmd+='-to %s '%parsed_args.to
    cmd+="%s"%d
    print ("Executing :%s"%cmd)
    os.system(cmd)

src=mutagen.id3.ID3(parsed_args.src, v2_version=3)
dest=mutagen.id3.ID3(parsed_args.dest, v2_version=3)
dest.delete()
dest.save(v2_version=3)
dest=mutagen.id3.ID3(parsed_args.dest, v2_version=3)
for k in src:
    dest[k] = src[k]
dest.save(v2_version=3)

if parsed_args.update:
    cmd = "mv %s %s"%(d,s)
    print ("Executing :%s"%cmd)
    os.system(cmd)

