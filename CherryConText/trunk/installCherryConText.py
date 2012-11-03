#!/usr/bin/env python

import subprocess
import os
import sys
import urllib2
import StringIO

user_home = os.path.expanduser("~")
os.chdir(user_home)
url = urllib2.urlopen("http://negex.googlecode.com/files/cherryConText-bootstrap2.py")
script = url.read()
f = os.path.join(user_home,"cherryConText-bootstrap.py")
fo = file(f,"w")
fo.write(script)
fo.close()
subprocess.call("python cherryConText-bootstrap.py CherryConText/CCTVE")
os.remove(f)
