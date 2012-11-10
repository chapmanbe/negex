#!/usr/bin/env python

import subprocess
import os
import sys
import urllib2
import StringIO
import shutil

user_home = os.path.expanduser("~")
os.chdir(user_home)
url = urllib2.urlopen("http://negex.googlecode.com/files/cherryConText-bootstrap2-win.py")
script = url.read()
f = os.path.join(user_home,"cherryConText-bootstrap.py")
fo = file(f,"w")
fo.write(script)
fo.close()
subprocess.call("python cherryConText-bootstrap.py CherryConText/CCTVE", shell=True)
os.remove(f)
shutil.copyfile(os.path.join("CherryConText","runme.py"),os.path.join("Desktop","runCherryConText.py"))
