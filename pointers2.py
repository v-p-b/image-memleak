#!/usr/bin/env python
import argparse
import os
import sys
import re

maps_re=re.compile(r"^([0-9a-f]+)-([0-9a-f]+) (.{4}) ([0-9a-f]+) ([0-9\:]+) ([0-9]+) *([^ ]*)$")

def parse_maps(f):
    ret=[]
    for l in f.readlines():
        m=maps_re.match(l.strip())
        if m is not None:
            ret.append((int(m.group(1),16),int(m.group(2),16),m.group(7))) # (START,END,NAME)
    return ret

def find_mapping(addr):
    for m in maps:
        if addr>=m[0] and addr<=m[1]:
            return m

def print_results(res):
    res_sorted=sorted(res.items(),key=lambda kv:(kv[1], kv[0]))
    for r in res_sorted[-1*args.num_results:]:
        found_map=""
        if maps is not None:
            mapping=find_mapping(r[0])
            if mapping is not None:
                found_map="[%x-%x %s]" % (mapping[0],mapping[1],mapping[2])
        print("%08x %d %s" % (r[0],r[1],found_map))

parser=argparse.ArgumentParser()
parser.add_argument("DAT",nargs="+",help="Extracted .DAT files")
parser.add_argument("--pointer-mask",type=str,default=None,help="Hexadecimal mask for pointer extraction (e.g. 0x7fdead000000)")
parser.add_argument("--maps",type=argparse.FileType('r'),default=None,help="Saved /proc/PID/maps")
parser.add_argument("--num-results", type=int,default=10)
args=parser.parse_args()
high={}
low={}

res={}
maps=None

if args.maps is not None:
    maps=parse_maps(args.maps)

for f in args.DAT:
    with open(f, "rb") as data:
        window=[None]*8
        i=0
        for v in data.read():
            window[i % len(window)] = v
            if i % len(window) == len(window)-1:
                val=0
                for j,w in enumerate(window):
                    val += w << (j*8)
                val = val & 0xffffffff0000
                if val & 0xff0000000000 == 0x7f0000000000:
                    if val not in high:
                        high[val]=1
                    else:
                        high[val]+=1
                if val < 0xbfffffff and val > 0xffffff:
                    if val not in low:
                        low[val]=1
                    else:
                        low[val]+=1
            
            i+=1
                    
print("LOW:")
print_results(low)
print("HIGH:")
print_results(high)


