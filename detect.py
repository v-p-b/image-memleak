import argparse
import math
import os
import statistics
import struct
import sys
import zlib
from PIL import Image

parser=argparse.ArgumentParser()

parser.add_argument("directory",type=str,help="Input directory")

args=parser.parse_args()

class Detector(object):
    def add_pixel(self, pixval):
        pass

    def get_result(self):
        pass

class CompressorDetector(Detector):
    def __init__(self):
        self.conv=[]
        self.size=0

    def add_pixel(self,pixval):
        self.conv.append(struct.pack("BBBB",*pixval))
        self.size+=len(pixval)

    def get_result(self):
        compressed=zlib.compress(b"".join(self.conv))
        return self.size/len(compressed)

class RareDotDetector(Detector):
    def __init__(self):
        self.size = 0
        self.dots = 0

    def add_pixel(self, pixval):
        for p in pixval:
            if p != 0:
                self.dots+=1
        self.size+=len(pixval)

    def get_result(self):
        if self.dots == 0:
            return -1.0
        return self.size/self.dots

class EntropyDetector(Detector):
    def __init__(self, block_size=64):
        self.data=[]
        self.block_size=block_size

    # From https://github.com/gcmartinelli/entroPy 
    def H(data):
        ''' Calculate the entropy of a given data block '''
        data = str(data)
        entropy = 0
        for x in range(256):
            p_x = data.count(chr(x))/len(data)
            if p_x > 0:
                entropy += -p_x*math.log(p_x, 2)
        return entropy

    # From https://github.com/gcmartinelli/entroPy
    def block_entropy(data, block_size):
        ''' Generator for calculating the entropy of a file,
            given a size for the data blocks '''
        for x in range(0, len(data)//block_size):
            start = x * block_size
            end = start + block_size
            yield EntropyDetector.H(data[start:end])

    def add_pixel(self, pixval):
        self.data.extend(pixval)

    def get_result(self):
        e=[]
        for b in EntropyDetector.block_entropy(self.data, self.block_size):
            e.append(b)
        #print("%f %f %f %f" % (sum(e)/len(e), statistics.median(e), min(e), max(e)))
        return max(e)


DETECTORS=[CompressorDetector(),RareDotDetector(),EntropyDetector()]

detectors_title=tuple(map(lambda c:c.__class__.__name__, DETECTORS))

#print(("Name\t"+"%s\t"*len(DETECTORS)) % detectors_title)
    
all_data=[[] for _ in DETECTORS]
results={}

for r, d, f in os.walk(args.directory):
    for img in f:
        DETECTORS=[CompressorDetector(),RareDotDetector(),EntropyDetector()]
        try:
            im=Image.open(os.path.join(args.directory,img))
            size=im.size
            pix=im.load()
            conv=[]
        except:
            sys.stderr.write("[-] Couldn't parse %s" % (img))
            continue

        for x in range(0,size[0]):
            for y in range(0,size[1]):
                p = pix[x,y]
                if isinstance(p, int):
                    p=[p]
                pixval=[0,0,0,0]
                for i,v in enumerate(p):
                    pixval[i]=v

                for o in DETECTORS:
                    o.add_pixel(pixval)

        res=[img]
        data=list(map(lambda o:o.get_result(), DETECTORS))
        res.extend(data)
        for i, d in enumerate(data):
            all_data[i].append(d)
        results[img]=data
        # print(("%s"+"\t%f"*len(DETECTORS)) % tuple(res) )

stats=[]
for r in all_data:
    stats.append((statistics.mean(r), statistics.median(r), statistics.pstdev(r)))
print(stats)

for i_name,i_data in results.items():
    outliers=[0]*len(DETECTORS)
    for i, d in enumerate(i_data):
        lower=stats[i][0]-stats[i][2]*0.5
        upper=stats[i][0]+stats[i][2]*0.5
        if d>upper or d<lower:
            outliers[i]=1
    print(i_name,outliers)

