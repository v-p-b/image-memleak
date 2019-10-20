#!/usr/bin/env python
import argparse
import os
import sys

res={}

for f in sys.argv[1:]:
    with open(f, "rb") as data:
        window=[None,None,None,None]
        i=0
        for v in data.read():
            window[i % len(window)] = v
            if i % len(window) == len(window)-1 and v == 0x7f:# and window[len(window)-2] != 0:
                val=0
                for j,w in enumerate(window):
                    val += w << (j*8)
                if val not in res:
                    res[val]=1
                else:
                    res[val]+=1
            i+=1

                    
res_sorted=sorted(res.items(),key=lambda kv:(kv[1], kv[0]))


for r in res_sorted[-50:-1]:
    print("%08x %d" % (r[0],r[1]))