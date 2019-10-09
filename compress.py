import argparse
import os
import struct
import zlib
from PIL import Image

parser=argparse.ArgumentParser()

parser.add_argument("directory",type=str,help="Input directory")

args=parser.parse_args()

for r, d, f in os.walk(args.directory):
    for img in f:
        im=Image.open(os.path.join(args.directory,img))
        size=im.size
        pix=im.load()
        conv=[]
        for x in range(0,size[0]):
            for y in range(0,size[1]):
                p = pix[x,y]
                if isinstance(p, int):
                    p=[p]
                pixval=[0,0,0,0]
                for i,v in enumerate(p):
                    pixval[i]=v
                    conv.append(struct.pack("BBBB",*pixval))
        compressed=zlib.compress(b"".join(conv))
        ratio=(size[0]*size[1]*4)/len(compressed)
        print("%s:\t%d\t%f" % (img,len(compressed),ratio))



