import argparse
import requests
import os
import re
import uuid
import urllib

parser = argparse.ArgumentParser()
parser.add_argument("--url",type=str, help="Upload url")
parser.add_argument("--iparam", type=str, help="Image parameter name")
parser.add_argument("--params", type=str, default="", help="Other parameters (as HTTP query string)")
parser.add_argument("--extract", type=str, default=None, help="Regex used to extract uploaded image info from response")
parser.add_argument("--prefix", type=str, default="", help="Image download URL prefix")
parser.add_argument("--postfix", type=str, default="", help="Image download URL postfix")
parser.add_argument("--indir", type=str, default="input", help="Input image directory")
parser.add_argument("--outdir", type=str, default="output", help="Output image directory")
args=parser.parse_args()

if args.extract is not None:
    extractor=re.compile(args.extract)

for r, d, f in os.walk(args.indir):
    for img in f:
        files={args.iparam:open(os.path.join(args.indir,img),"rb")}
        print("[*] Sending %s" % img)
        r=requests.post(args.url,files=files, data=urllib.parse.parse_qs(args.params), verify=False, allow_redirects=False)
        m=None
        part=None
        if extractor is not None:
            m=extractor.search(r.text)
            if m is None:
                print("[-] Couldn't extract from '%s'" % (r.text))
                continue
        if m is not None:
            part=m.group(1)
        new_url="%s%s%s" % (args.prefix,part,args.postfix)
        print("[*] Sending request to %s" % (new_url))
        ir=requests.get(new_url)
        out_fname="%s_%s.bin" % (img, uuid.uuid1())
        with open(os.path.join(args.outdir, out_fname), "wb") as out:
            out.write(ir.content)
            print("[+] %s saved" % (out_fname))


