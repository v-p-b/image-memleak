import argparse
import os
import struct
import zlib
from PIL import Image


parser=argparse.ArgumentParser()

parser.add_argument("png",type=argparse.FileType("rb"), nargs="+", help="PNG file to fill")
parser.add_argument("--outdir",type=str)
args=parser.parse_args()

for png in args.png:
    with png as infile:
        print("[*] Processing %s" % (png.name))
        data = infile.read()
        data_out = bytearray(data)

        last_idat = data_out.find(b"IDAT")
        
        while last_idat != -1:
            idat_size=struct.unpack(">I", data_out[last_idat-4:last_idat])[0]
            print("[*] Found IDAT at 0x%x Size: 0x%x" % (last_idat, idat_size))
            idat=data_out[last_idat+4:last_idat+4+idat_size]
            try:
                idat_raw=zlib.decompress(idat)
                fill_raw=b'\x00'*len(idat_raw)
                fill=zlib.compress(fill_raw)
                print("[*] Fill size: %x" % (len(fill)))
                print("[*] CRC: %x" % (zlib.crc32(b"IDAT"+fill) & 0xffffffff))
                data_out = data_out[0:last_idat-4] + struct.pack(">I",len(fill)) + b"IDAT" + fill + struct.pack(">I",zlib.crc32(b"IDAT"+fill) & 0xffffffff) + data_out[last_idat+4+idat_size+4:]

            except zlib.error:
                print("[-] zlib decompression error while processing %s" % (png.name))
                
                
            last_idat=data_out.find(b"IDAT", last_idat+1)

        out_name=None
        if ".png" in png.name:
            out_name=png.name.replace('.png','.filled.png')
        else:
            out_name=png.name+'.filled.png'
        if args.outdir is not None:
            out_name=os.path.join(args.outdir,os.path.basename(out_name))
        with open(out_name,"wb") as out:
            out.write(data_out)



