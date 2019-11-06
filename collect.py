#!/usr/bin/env python
import argparse
import binascii
import requests
import os
import re
import uuid
import urllib
import time
from PIL import Image

def decompress(imgfile, outdir, pattern=None):
    im=None
    size=None
    pix=None

    try:
        im=Image.open(os.path.join(outdir,imgfile))
        size=im.size
        pix=im.load()
    except:
        raise
        print("[-] Unable to open/parse '%s'" % (os.path.join(outdir,imgfile)))
        exit()

    output_ba=bytearray()

    n = 0
    pattern_window=bytearray()
    found = False
    if pattern is None:
        found = True
    for y in range(0,size[1]):
        for x in range(0,size[0]):
            p = pix[x,y]
            if isinstance(p, int):
                p=[p]
            for b in p:
                pattern_window.append(b)
                if pattern is not None and len(pattern_window) == len(pattern):
                    #print(repr(pattern_window))
                    if pattern_window == pattern:
                        found=True
                        pattern = None
                    pattern_window=bytearray()
                #if b == 0 or b == 0xff:
                #    continue
                output_ba.append(b)
    if not found:
        print("[*] Deleting %s" % (os.path.join(outdir,imgfile)))
        os.unlink(os.path.join(outdir,imgfile))
        return
    with open(os.path.join(outdir, imgfile+".dat"),"wb") as out:
        print("[+] PATTERN FOUND!")
        out.write(output_ba)

parser = argparse.ArgumentParser()
parser.add_argument("--url",type=str, help="Upload url")
parser.add_argument("--iparam", type=str, help="Image parameter name")
parser.add_argument("--params", type=str, default="", help="Other parameters (as HTTP query string)")
parser.add_argument("--addfile",type=str,default=None, help="Additional file to send with the multipart request")
parser.add_argument("--extract", type=str, default=None, help="Regex used to extract uploaded image info from response")
parser.add_argument("--prefix", type=str, default="", help="Image download URL prefix")
parser.add_argument("--postfix", type=str, default="", help="Image download URL postfix")
parser.add_argument("--indir", type=str, default="input", help="Input image directory")
parser.add_argument("--outdir", type=str, default="output", help="Output image directory")
parser.add_argument("--sleep", type=float, default=0.0)
parser.add_argument("--repeat", type=int, default=1)
parser.add_argument("--decompress", action="store_true")
parser.add_argument("--nokeep", action="store_true")
parser.add_argument("--pattern", default=None, help="Only save responses containing pattern")

args=parser.parse_args()

extractor=None
if args.extract is not None:
    extractor=re.compile(args.extract)

for _ in range(0,args.repeat):
    for r, d, f in os.walk(args.indir):
        for img in f:
            time.sleep(args.sleep)
            files={args.iparam:open(os.path.join(args.indir,img),"rb")}
            if args.addfile is not None:
                files["addfile"]=open(args.addfile,"rb")
            print("[*] Sending %s" % img)
            r=None
            try:
                r=requests.post(args.url,files=files, data=urllib.parse.parse_qs(args.params), verify=False, allow_redirects=False)
            except requests.exceptions.ConnectionError :
                print("[-] Upload request failure!")
                continue
            if args.nokeep:
                continue
            m=None
            part=None
            resp_img=None
            if extractor is not None:
                m=extractor.search(r.text)
                if m is None:
                    print("[-] Couldn't extract from '%s'" % (r.text))
                    continue
            if m is not None:
                part=m.group(1)
            if part is not None:
                new_url="%s%s%s" % (args.prefix,part,args.postfix)
                print("[*] Sending request to %s" % (new_url))
                try:
                    ir=requests.get(new_url)
                    resp_img=ir.content
                except:
                    print("[-] Connection error while downloading image")
                    continue
            if resp_img is None:
                resp_img = r.content
            out_fname="%s_%s.bin" % (img, uuid.uuid1())
            with open(os.path.join(args.outdir, out_fname), "wb") as out:
                out.write(resp_img)
                print("[*] %s saved" % (out_fname))
            if args.decompress:
                pattern_decoded=None
                if args.pattern:
                    pattern_decoded=binascii.unhexlify(args.pattern)
                decompress(out_fname, args.outdir, pattern_decoded)


