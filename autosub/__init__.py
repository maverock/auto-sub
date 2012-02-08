import Config
import logging.handlers

ROOTPATH=None
FALLBACKTOENG=None
DOWNLOADENG=None
SUBENG=None
LOGFILE=None
SUBNL=None
LOGLEVEL=None
LOGLEVELCONSOLE=None
LOGSIZE=None
LOGNUM=None
SKIPSHOW=None
SKIPSHOWUPPER=None
USERNAMEMAPPING=None
USERNAMEMAPPINGUPPER=None
NAMEMAPPING=None
NAMEMAPPINGUPPER=None
SHOWID_CACHE=None
POSTPROCESSCMD=None
CONFIGFILE=None
PATH=None

TODOWNLOADQUEUE=None
WANTEDQUEUE=None
WANTEDQUEUELOCK=False
TODOWNLOADQUEUELOCK=False
LASTESTDOWNLOAD=None

RSSURL=None
WIPURL=None
APIKEY=None
API=None

SCHEDULERSCANDISK=None
SCHEDULERCHECKSUB=None
SCHEDULERCHECKRSS=None
SCHEDULERDOWNLOADSUBS=None
SCHEDULERWIPSTATUS=None

SCANDISK=None
CHECKSUB=None
CHECKRSS=None
DOWNLOADSUBS=None
WIPSTATUS=None

WEBSERVERIP=None
WEBSERVERPORT=None

DAEMON=None

def Initialize():
    global ROOTPATH, FALLBACKTOENG, SUBENG, LOGFILE, SUBNL, LOGLEVEL, \
    SUBNL, LOGLEVEL, LOGLEVELCONSOLE, LOGSIZE, LOGNUM, SKIPSHOW, SKIPSHOWUPPER, \
    USERNAMEMAPPING, USERNAMEMAPPINGUPPER, NAMEMAPPING, NAMEMAPPINGUPPER, \
    SHOWID_CACHE, POSTPROCESSCMD, CONFIGFILE, WORKDIR, \
    TODOWNLOADQUEUE, WANTEDQUEUE, \
    RSSURL, APIKEY, API, WIPURL, \
    SCHEDULERSCANDISK, SCHEDULERCHECKSUB, SCHEDULERCHECKRSS, SCHEDULERDOWNLOADSUBS, \
    SCHEDULERWIPSTATUS, \
    DAEMON
    
    TODOWNLOADQUEUE = []
    WANTEDQUEUE = []

    RSSURL = "http://www.bierdopje.com/rss/subs/nl"
    APIKEY = "AFC34E2C2FE8B9F7"
    WIPURL = "http://www.bierdopje.com/wip/overview"
    
    SCHEDULERSCANDISK=3600  #run scandisk every hour
    SCHEDULERCHECKSUB=28800 #run checksub every 8 hours
    SCHEDULERCHECKRSS=900   #run checkrss every 15 minutes
    SCHEDULERDOWNLOADSUBS=1  #run downloadsubs every second
    SCHEDULERWIPSTATUS=86400 #run wipstatus every day
    if CONFIGFILE==None:
        CONFIGFILE = "config.properties"
    
    Config.ReadConfig(CONFIGFILE)
    API = "http://api.bierdopje.com/%s/" %APIKEY
    
def initLogging(logfile):
    global LOGLEVEL, LOGSIZE, LOGNUM, LOGLEVELCONSOLE, \
    DAEMON
    
    # initialize logging
    # A log directory has to be created below the start directory
    log = logging.getLogger("thelogger")
    log.setLevel(LOGLEVEL)

    log_script = logging.handlers.RotatingFileHandler(logfile, 'a', LOGSIZE, LOGNUM)
    log_script_formatter=logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
    log_script.setFormatter(log_script_formatter)
    log_script.setLevel(LOGLEVEL)
    log.addHandler(log_script)
    
    #CONSOLE log handler
    if DAEMON!=True:
        console = logging.StreamHandler()
        console.setLevel(LOGLEVELCONSOLE)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
        console.setFormatter(formatter)
        log.addHandler(console)
    
    return log