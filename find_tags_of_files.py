#!/usr/bin/python

from __future__ import print_function
import subprocess
import sys
import re
import argparse

ok_tags_values=['TIT2', 'TALB', 'TPE1',  'TPE2',      'TCON', 'TRCK', 'APIC','TYER','V1']
ok_tags_names= ['Title','Album','Artist','Alb Artist','Genre','Track','Pic', 'Year','V1']
ok_tags_default_values= [25,25,25,25,25,10,10,3,3]

def initialize():
  ok_tags = {}
  for tags,tag_des,format_len in zip(ok_tags_values,ok_tags_names,ok_tags_default_values):
    ok_tags[tags] = (tag_des,format_len)
  return ok_tags


def grab_tags_of_file(max_lens, filename):
  ''' Given a filename, grabs all the tags in it, and return a (success/fail,dict-of-tags-to-values)

      max_lens is a dict of (tags->max-len-of-values) . This is updated in case this file's info exceeds the existing max-len
  '''
  tags = {}
  v2_frame_pattern=r'([A-Z0-9]{4}) \(.*: (.*)'
  a = subprocess.Popen(["id3v2","-l",filename],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  op_out,op_err = a.communicate()
  a.wait()
  if op_err:
    return (0,op_err)
  lines = op_out.split('\n')
  for l in lines:
    if not l:
      continue
    if 'No ID3 tag' in l:
      tags['V1'] = 0
      continue
    if 'No ID3v2 tag' in l:
      continue
    if 'id3v2 tag info for' in l:
      continue
    if 'id3v1 tag info for' in l:
      tags['V1'] = 1
      continue
    if 'Title  :' in l and 'Artist:' in l:
      continue
    if 'Album  :' in l and 'Year:' in l and 'Genre:' in l:
      continue
    if 'Comment:' in l and tags['V1'] == 1:
      continue
    if 'No ID3v1 tag' in l:
      tags['V1'] = 0
      continue
    v2_frame = re.search(v2_frame_pattern, l)
    if v2_frame:
      t = v2_frame.group(1)
      l = len(v2_frame.group(2))
      tags[t] = v2_frame.group(2)
      if t in max_lens:
        if l > max_lens[t]:
          max_lens[t] = l
      else:
        max_lens[t] = l
    else:
      err="Unknown line: %s"%l
      return (0,err)
  l = len(filename)
  if l > max_lens["FileName"]:
    max_lens["FileName"] = l
  return (1,tags)

def print_tags_from_all_files(ok_tags, max_len, all_files, info, verbose):
  format_str="%%-%ds |"%max_len["FileName"]
  for i in ok_tags_values:
    if i in max_len:
      val = max_len[i]
    else:
      val = ok_tags[i][1]
    format_str += " %%-%ds |"%val
  format_str += " %s"
  #format_str="%-50s | %-25s | %-25s | %-25s | %-25s | %-25s | %-10s | %-10s | %-3s | %-3s | %s"
  title=format_str%("FileName","Title","Album","Artist","Album Artist","Genre","Trk","Pic","Year","V1","Extras")
  print(title)
  for i in all_files:
    file_info = info[i]
    file_values = []
    for j in ok_tags_values:
      if j in file_info:
        file_values.append(file_info[j])
        file_info.pop(j,None)
      else:
        file_values.append("***")
    extras = ""
    for j in file_info.keys():
      extras += j
      if verbose:
        extras += ":" + file_info[j] + ","
      extras += " "
    final = format_str%(i,file_values[0],file_values[1],file_values[2],file_values[3],file_values[4],
                          file_values[5],file_values[6],file_values[7],file_values[8],extras)
    print(final)



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-v","--verbose", help="print extra tags in verbose", action="store_true")       # captures if --verbosity present or not in
  parser.add_argument("-f","--filelist", help="use the args as a file which has a list of files", action="store_true")       # captures if --verbosity present or not in
  parser.add_argument("files", help="mp3 files", nargs="+")
  args = parser.parse_args()

  ok_tags = initialize()
  verbose = 0
  if args.verbose:
    verbose = 1
  all_files = []
  all_files_info = {}
  input_files = []
  if args.filelist:
    for i in args.files:
      with open(i,'r') as fd:
        for j in fd:
          input_files.append(j.strip())
  else:
    input_files = args.files
  max_lens = {}
  max_lens["FileName"] = 0
  for i in input_files:
    (ok,tags) = grab_tags_of_file(max_lens,i)
    if ok != 1:
      print("Got error in file %s, :%s"%(i,tags),file=sys.stderr)
      continue
    else:
      all_files.append(i)
      all_files_info[i] = tags
  print_tags_from_all_files(ok_tags, max_lens,all_files,all_files_info,verbose)
