import autosub.AutoSub

import sys
import getopt
import os
import signal

signal.signal(signal.SIGINT, autosub.AutoSub.signal_handler)
signal.signal(signal.SIGTERM, autosub.AutoSub.signal_handler)

help_message = '''
Usage:
    -h (--help)    Prints this message
    -c | --config= Forces AutoSub.py to use a configfile other than ./config.properties

Example:
    python AutoSub.py
    python AutoSub.py -c/home/user/config.properties
    python AutoSub.py --config=/home/user/config.properties
'''

# TODO: comments in everyfile

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args= getopt.getopt(argv[1:], "hc:", ["help","config="])
        except getopt.error, msg:
            raise Usage(msg)
    
        # option processing
        for option, value in opts:
            if option in ("-h", "--help"):
                raise Usage(help_message)
            elif option in ("-c", "--config"):
                autosub.CONFIGFILE = value
    
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2
    
    #load configuration
    if os.path.isfile('config.properties.dev'):
        autosub.CONFIGFILE='config.properties.dev'
    print "AutoSub: Initializing variables and loading config"
    autosub.Initialize()
    
    #change to the new work directory
    if autosub.WORKDIR!=None:
        print "AutoSub: Changing to workdirectory"
        os.chdir(autosub.WORKDIR)
    
    print "AutoSub: Changing output to log"
    log = autosub.initLogging(autosub.LOGFILE)
    
    log.info("AutoSub: Starting threads")
    autosub.AutoSub.start()
    
    log.info("AutoSub: threads started, going into a loop to keep the main thread going")
    
    while True:
        pass
if __name__ == "__main__":
    sys.exit(main())

#while True:
    #if not downloadSubs.thread.isAlive() or not downloadSubs.thread.isAlive() or not localdisk.thread.isAlive() or not downloadSubs.thread.isAlive():
    #    print traceback.format_exc()
    #    os._exit(1)
#    time.sleep(1)