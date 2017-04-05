#!/usr/bin/python
# *****BatteryMonitor store summary data summary.py*****
# Copyright (C) 2014 Simon Richard Matthews
# Project loaction https://github.com/simat/BatteryMonitor
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys
from os import rename
import time
from shutil import copy as filecopy
from copy import deepcopy
from ast import literal_eval
from ConfigParser import SafeConfigParser
from config import config, loadconfig
numiin = len(config['CurrentInputs'])
numcells = config['battery']['numcells']

summaryfile = SafeConfigParser()

def tail(file, n=1, bs=1024):
    f = open(file)
    f.seek(-1,2)
    l = 1-f.read(1).count('\n') # If file doesn't end in \n, count it anyway.
    B = f.tell()
    while n >= l and B > 0:
            block = min(bs, B)
            B -= block
            f.seek(B, 0)
            l += f.read(block).count('\n')
    f.seek(B, 0)
    l = min(l,n) # discard first (incomplete) line if l > n
    lines = f.readlines()[-l:]
    f.close()
    return lines

def getavi():
  istr=""
  avi = [ 0.0 for i in range(numiin)]  
  endlog=tail(config['files']['logfile'],11)
  for line in range(10):
    lineargs = str(endlog[line]).split(' ')
    for iin in range(numiin):
      avi[iin] = avi[iin] + float(lineargs[1+numcells+2+iin])/10
  for iin in range(numiin):
    istr =istr+str(round(avi[iin],3)) + ", "
  print 'Average readings for last 100 seconds: ' + istr
  loadconfig()
  print 'gain from config file: ' + str(config['calibrate']['currentgain'])
  return avi


def geti():
  try:
    summaryfile.read(config['files']['summaryfile'])
  except IOError:
    pass
  iin=literal_eval(summaryfile.get('current','currentmax'))
  iprint = ''
  for i in range(numiin):
    iprint = iprint + str(i+1) + '=' + str(iin[i]).ljust(5,'0') + ', '
  print 'Readings from summary: ' + iprint

  
def main():
  print 'Usage: At > prompt enter current input channel number to change then [Enter] key'
  print '       Pressing just the [Enter] key will display the latest current readings, type ^C to exit'
  print '       Make sure the Battery Monitoring software is running otherwise the summary file will not be current'   
  while True:
    try:
#      time.sleep(60.0)
      geti()
      what = raw_input(">")
      if len(what)>0:
        avi=getavi()
        reali = input("Input " + what + " multimeter reading ")
        what=int(what)
        config['calibrate']['currentgain'][what-1] = config['calibrate']['currentgain'][what-1]*reali/avi[what-1]
        print 'Recalculated gain: ' + str(config['calibrate']['currentgain'])
        batconfigdata=SafeConfigParser()
        batconfigdata.read('battery.cfg')
        batconfigdata.set('calibrate','currentgain',str(config['calibrate']['currentgain']))
        with open('battery.cfg', 'w') as batconfig:
          batconfigdata.write(batconfig)
        batconfig.closed



    except KeyboardInterrupt:
      break

if __name__ == "__main__":
  main()
