#!/usr/bin/env python
import subprocess
import os

user_home = os.path.expanduser("~")
if( os.name == 'posix' ):
    bloc = 'bin'
else:
    bloc = 'Scripts'
os.chdir(os.path.join(user_home,"CherryConText"))
# I need to change this script to invoke the virtualenv first
subprocess.call("""%s %s"""%(os.path.join("CCTVE",bloc,"python"),
                             "__init__.py"),shell=True)
