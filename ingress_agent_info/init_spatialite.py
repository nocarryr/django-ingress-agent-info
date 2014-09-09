#!/usr/bin/env python

import os
import subprocess
from ingress_agent_info.settings import DATABASES

def main():
    if DATABASES['default']['ENGINE'].split('.')[-1] != 'spatialite':
        return
    filename = DATABASES['default']['NAME']
    if os.path.exists(filename):
        raise Exception('database already exists. please delete the file.')
    cmd_str = 'spatialite %s "SELECT InitSpatialMetaData();"' % (filename)
    o = subprocess.check_output(cmd_str, shell=True)
    print o
    print 'spatialite initialized.  syncdb can now be run'

if __name__ == '__main__':
    main()
