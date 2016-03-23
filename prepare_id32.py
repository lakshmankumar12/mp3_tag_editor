#!/usr/bin/python

from __future__ import print_function
import sys


title_translation = {
'Title'        : 'TIT2',
'Album'        : 'TALB',
'Artist'       : 'TPE1',
'Album Artist' : 'TPE2',
'Genre'        : 'TCON',
'Trk'          : 'TRCK',
'Year'         : 'TYER',
'FileName'     : None,
'Pic'          : None,
'V1'           : None,
'Extras'       : 'Extras'
}

def process_extras(v, name):
  cmd_prefix = "id3v2 -2"
  tags = v.split()
  for i in tags:
    result = cmd_prefix + ' --remove-frame "%s" "%s"'%(i,name)
    print(result)

def process_id3(filename):
  f=open(filename,"r")
  head=next(f)
  ids = [ title_translation[i.strip()] for i in head.split('|') ]
  for tracks in f:
    values = [ i.strip() for i in tracks.split('|') ]
    cmd='id3v2 -2 '
    for t,v in zip(ids[1:],values[1:]):
      if t == None: continue
      if v == '***': continue
      if t == 'Extras':
        process_extras(v, values[0])
        continue
      if t == 'TCON':
        found = v.find('(255)')
        if found != -1:
          v=v[:found]
          v=v.strip()
      cmd += '--%s "%s" '%(t,v)
    cmd += ' "%s"'%values[0]
    print(cmd)

usage='''
The file should have a title line
and values line'''

if __name__ == '__main__':
  try:
    process_id3(sys.argv[1])
  except Exception,e:
    print("Usage %s <file-with-values>"%sys.argv[0])
    print(usage)
    print("Got exception with err:%s"%str(e))
