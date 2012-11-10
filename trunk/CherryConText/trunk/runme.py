#!/usr/bin/env python
import subprocess
import os
if( os.name == 'posix' ):
    bloc = 'bin'
else:
    bloc = 'Scripts'

# I need to change this script to invoke the virtualenv first
subprocess.call("""%s __init__.py"""%os.path.join("CCTVE",bloc,"python"),shell=True)
