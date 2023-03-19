#!/usr/bin/python
import os
import socket
import time
#============================================#
logfile = '/home/xinyx/Desktop/log.txt'

# ======================================================================================================== #
#                                                Functions                                                 #
# ======================================================================================================== #

def internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False

def chkproc(procname):
    pse_cmd = 'ps -f | grep ' + str(procname) + ' | grep -v grep'
    chk = os.popen(pse_cmd).read()
    if chk != '':
        print("Process " + procname + " is running.")
        result = True
    else:
        print("Process " + procname + " is not running.")
        result = False
    print(chk)
    return result

def logme(var,file):
    loadfile = open(file, '+a')
    loadfile.write(str(var) + '\n')
    loadfile.close()

while not internet():
    status = "No internet yet, wait a bit"
    logme(status,logfile)
    time.sleep(10)
status = "There is internet now"
logme(status,logfile)

while True:
    if not chkproc('barc_v2'):
        # Process not running, attempting to relaunch
        print("Process not running, attempt to relaunc")
        os.popen('/usr/bin/python3 /home/xinyx/barc/barc_v2.py &').read()
    else:
        print("Process still running, no action required")
    time.sleep(15)