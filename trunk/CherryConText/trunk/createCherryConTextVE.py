#!/usr/bin/env python

import virtualenv, textwrap

output = virtualenv.create_bootstrap_script(textwrap.dedent("""
import os
import sys

import subprocess
import urllib2
from zipfile import ZipFile
import StringIO

user_home = os.path.expanduser("~")
cfiles = os.path.join(user_home,"CherryConText.zip")

def after_install(options, home_dir):
    if( os.name == 'posix' ):
        print "Installing on a posix system"
        bloc = 'bin'
    else:
        print "Assuming installation on a Windows system"
        bloc = 'Scripts'
    print "Installing virtualenv"
    subprocess.call([join(home_dir,bloc,'pip'), 'install', 'cherrypy'])
    subprocess.call([join(home_dir,bloc,'pip'), 'install', 'django'])
    subprocess.call([join(home_dir,bloc,'pip'), 'install', 'pyConTextNLP'])
    url = urllib2.urlopen("http://negex.googlecode.com/files/CherryConText.zip")
    zipfile = ZipFile(StringIO.StringIO(url.read()))
    zipfile.extractall(user_home)
"""))
f = open('cherryConText-bootstrap2.py','w').write(output)





