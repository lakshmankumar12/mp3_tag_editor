#!/usr/bin/python

from __future__ import print_function
import sys
import subprocess
import argparse
import os
import re
import shutil
from find_tags_of_files import initialize
from find_tags_of_files import grab_tags_of_file

parser = argparse.ArgumentParser()
parser.add_argument("--ss", help="start time in HH:MM:SS")
parser.add_argument("--to", help="end time in HH:MM:SS")
parser.add_argument("file",  help="file")
parsed_args = parser.parse_args()

if not parsed_args.ss and not parsed_args.to:
    print("You should supply at least a start or end time");
    sys.exit(1)

ok_tags = initialize()
maxlen_dict = {}
maxlen_dict["FileName"] = 0
(ok,tags) = grab_tags_of_file(maxlen_dict, parsed_args.file)

temp_file = "temp.mp3"
temp_cover_dir = "temp_cover_dir"

if os.path.isfile(temp_file):
    os.remove(temp_file)

if os.path.isdir(temp_cover_dir):
    shutil.rmtree(temp_cover_dir)

cmd = ["avconv","-i",parsed_args.file]
if parsed_args.ss:
    cmd.append("-ss")
    cmd.append(parsed_args.ss)
if parsed_args.to:
    cmd.append("-to")
    cmd.append(parsed_args.to)
cmd.extend(["-acodec","copy",temp_file])
print("Executing:",end="")
print(' '.join(cmd))
a = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
op_out,op_err = a.communicate()
a.wait()
print ("Got:%s, err:%s"%(op_out,op_err))

cmd = ["id3v2","-2"]
for i in tags:
    if i == "V1":
        continue
    if i == "APIC":
        continue
    if i == "TCON":
        tags[i] = re.sub("\s+\(.*\)","",tags[i])
    cmd.append("--"+i)
    cmd.append(str(tags[i]))
cmd.append(temp_file)
print("Executing:",end="")
print(' '.join(cmd))
a = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
op_out,op_err = a.communicate()
a.wait()
print ("Got:%s, err:%s"%(op_out,op_err))

os.makedirs(temp_cover_dir)
cmd = ['eyeD3','--write-images',temp_cover_dir,parsed_args.file]
print("Executing:",end="")
print(' '.join(cmd))
a = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
op_out,op_err = a.communicate()
a.wait()
print ("Got:%s, err:%s"%(op_out,op_err))

a=os.path.join(temp_cover_dir,"FRONT_COVER.jpg")
if not os.path.exists(a):
    print("Oops! FRONT_COVER.jpg wasn't extracted")
else:
    cmd = ['eyeD3','-2','--add-image',a+':FRONT_COVER',temp_file]
    print("Executing:",end="")
    print(' '.join(cmd))
    a = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    op_out,op_err = a.communicate()
    a.wait()
    print ("Got:%s, err:%s"%(op_out,op_err))

os.rename(parsed_args.file,parsed_args.file[:-4]+"-back.mp3")
os.rename(temp_file, parsed_args.file)
