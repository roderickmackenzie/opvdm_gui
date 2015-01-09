#!/usr/bin/python

import sys
import zipfile

archive=sys.argv[1]
infile=sys.argv[2]
new_name=sys.argv[3]

zf = zipfile.ZipFile(archive, mode='a')
try:
    zf.write(infile, arcname=new_name)
finally:
    zf.close()
