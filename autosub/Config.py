# Autosub Config.py - http://code.google.com/p/auto-sub/
#
# The Autosub config Module
#

# python 2.5 support
from __future__ import with_statement

import os
import logging

from ConfigParser import SafeConfigParser

import autosub

# Autosub specific modules

# Settings -----------------------------------------------------------------------------------------------------------------------------------------
# Location of the configuration file:
# configfile = "config.properties"
# Set the logger
log = logging.getLogger('thelogger')
#/Settings -----------------------------------------------------------------------------------------------------------------------------------------

# TODO: Webserver config, basic are done. CherryPy logging still needs a file only


def ReadConfig(configfile):
    """
    Read the config file and set all the variables.
    """
    edited = False

    # Read config file
    cfg = SafeConfigParser()
    try:
        cfg.read(configfile)
    except:
        print "***************************************************************************"
        print "Config ERROR: Not a valid configuration file! Using default values instead!"
        print "***************************************************************************"

    if cfg.has_section('config'):
        if cfg.has_option('config', 'path'):
            autosub.PATH = cfg.get('config', 'path')
        else:
            print "Config ERROR: Variable PATH is missing. This is required! Using current working directory instead."
            autosub.PATH = os.getcwd()

        if cfg.has_option('config', 'downloadeng'):
            autosub.DOWNLOADENG = cfg.getboolean('config', 'downloadeng')
        else:
            autosub.DOWNLOADENG = False

        if cfg.has_option('config', 'minmatchscore'):
            autosub.MINMATCHSCORE = int(cfg.get('config', 'minmatchscore'))
        else:
            autosub.MINMATCHSCORE = 0

        if cfg.has_option('config', 'minmatchscoreRSS'):
            autosub.MINMATCHSCORERSS = int(cfg.get('config', 'minmatchscorerss'))
        else:
            autosub.MINMATCHSCORERSS = 4

        if cfg.has_option('config', 'scandisk'):
            autosub.SCHEDULERSCANDISK = int(cfg.get('config', 'scandisk'))
        else:
            autosub.SCHEDULERSCANDISK = 3600

        if cfg.has_option('config', 'checksub'):
            autosub.SCHEDULERCHECKSUB = int(cfg.get('config', 'checksub'))
            # CHECKSUB may only be runed 6 times a day, to prevent the API key from being banned
            # If you want new subtitles faster, you should decrease the CHECKRSS time
            if autosub.SCHEDULERCHECKSUB < 21600:
                print "Config WARNING: checksub variable is lower then 21600! This is not allowed, this is to prevent our API-key from being banned."
                autosub.SCHEDULERCHECKSUB = 21600  # Run every 6 hours
        else:
            autosub.SCHEDULERCHECKSUB = 28800  # Run every 8 hours

        if cfg.has_option('config', 'checkrss'):
            autosub.SCHEDULERCHECKRSS = int(cfg.get('config', 'checkrss'))
            # Because of the http timeout it is not recommened to set checkrss lower then 1 minute
            if autosub.SCHEDULERCHECKRSS < 60:
                print "Config WARNING: checkrss variable is lower then 60. Because of http timeout it is not recommended to set it below 60 seconds."
                autosub.SCHEDULERCHECKRSS = 60  # Run every minute
        else:
            autosub.SCHEDULERCHECKRSS = 900  # Run every 15 minutes

        if cfg.has_option('config', 'downloadsubs'):
            autosub.SCHEDULERDOWNLOADSUBS = int(cfg.get('config', 'downloadsubs'))
        else:
            autosub.SCHEDULERDOWNLOADSUBS = 1  # Run every second

        if cfg.has_option("config", "ROOTPATH"):
            autosub.ROOTPATH = cfg.get("config", "ROOTPATH")
        else:
            print "Config ERROR: Variable ROOTPATH is missing. This is required! Using current working directory instead."
            autosub.ROOTPATH = os.getcwd()

        if cfg.has_option("config", "FALLBACKTOENG"):
            autosub.FALLBACKTOENG = cfg.getboolean("config", "FALLBACKTOENG")
        else:
            autosub.FALLBACKTOENG = True

        if cfg.has_option("config", "SUBENG"):
            autosub.SUBENG = cfg.get("config", "SUBENG")
        else:
            autosub.SUBENG = 'en'

        if cfg.has_option("config", "SUBNL"):
            autosub.SUBNL = cfg.get("config", "SUBNL")
        else:
            autosub.SUBNL = ""

        if cfg.has_option("config", "workdir"):
            autosub.PATH = cfg.get("config", "workdir")
            print "Config WARNING: Workdir is an old variable. Replace it with 'path'."

        if cfg.has_option("config", "LOGFILE"):
            autosub.LOGFILE = cfg.get("config", "LOGFILE")
        else:
            print "Config ERROR: Variable LOGFILE is missing. This is required! Using 'AutoSubService.log' instead."
            autosub.LOGFILE = "AutoSubService.log"

        if cfg.has_option("config", "POSTPROCESSCMD"):
            autosub.POSTPROCESSCMD = cfg.get("config", "POSTPROCESSCMD")
        else:
            autosub.POSTPROCESSCMD = False

    else:
        # config section is missing
        print "Config ERROR: Config section is missing. This is required, it contains vital options! Using default values instead!"
        print "Config ERROR: Variable ROOTPATH is missing. This is required! Using current working directory instead."
        autosub.PATH = os.getcwd()
        autosub.DOWNLOADENG = False
        autosub.MINMATCHSCORE = 0
        autosub.MINMATCHSCORERSS = 4
        autosub.SCHEDULERSCANDISK = 3600
        autosub.SCHEDULERCHECKSUB = 28800
        autosub.SCHEDULERCHECKRSS = 900
        autosub.SCHEDULERDOWNLOADSUBS = 1
        print "Config ERROR: Variable ROOTPATH is missing. This is required! Using current working directory instead."
        autosub.ROOTPATH = os.getcwd()
        autosub.FALLBACKTOENG = True
        autosub.SUBENG = 'en'
        autosub.SUBNL = ""
        print "Config ERROR: Variable LOGFILE is missing. This is required! Using 'AutoSubService.log' instead."
        autosub.LOGFILE = "AutoSubService.log"
        autosub.POSTPROCESSCMD = False

    if cfg.has_section('logfile'):
        if cfg.has_option("logfile", "LOGLEVEL"):
            autosub.LOGLEVEL = cfg.get("logfile", "LOGLEVEL")
            if autosub.LOGLEVEL.lower() == 'error':
                autosub.LOGLEVEL = logging.ERROR
            elif autosub.LOGLEVEL.lower() == "warning":
                autosub.LOGLEVEL = logging.WARNING
            elif autosub.LOGLEVEL.lower() == "debug":
                autosub.LOGLEVEL = logging.DEBUG
            elif autosub.LOGLEVEL.lower() == "info":
                autosub.LOGLEVEL = logging.INFO
            elif autosub.LOGLEVEL.lower() == "critical":
                autosub.LOGLEVEL = logging.CRITICAL
        else:
            autosub.LOGLEVEL = logging.INFO

        if cfg.has_option("logfile", "loglevelconsole"):
            autosub.LOGLEVELCONSOLE = cfg.get("logfile", "loglevelconsole")
            if autosub.LOGLEVELCONSOLE.lower() == 'error':
                autosub.LOGLEVELCONSOLE = logging.ERROR
            elif autosub.LOGLEVELCONSOLE.lower() == "warning":
                autosub.LOGLEVELCONSOLE = logging.WARNING
            elif autosub.LOGLEVELCONSOLE.lower() == "debug":
                autosub.LOGLEVELCONSOLE = logging.DEBUG
            elif autosub.LOGLEVELCONSOLE.lower() == "info":
                autosub.LOGLEVELCONSOLE = logging.INFO
            elif autosub.LOGLEVELCONSOLE.lower() == "critical":
                autosub.LOGLEVELCONSOLE = logging.CRITICAL
        else:
            autosub.LOGLEVELCONSOLE = logging.ERROR

        if cfg.has_option("logfile", "LOGSIZE"):
            autosub.LOGSIZE = int(cfg.get("logfile", "LOGSIZE"))
        else:
            autosub.LOGSIZE = 1000000

        if cfg.has_option("logfile", "LOGNUM"):
            autosub.LOGNUM = int(cfg.get("logfile", "LOGNUM"))
        else:
            autosub.LOGNUM = 3

    else:
        # Logfile section is missing, so set defaults for all options
        autosub.LOGLEVEL = logging.INFO
        autosub.LOGLEVELCONSOLE = logging.ERROR
        autosub.LOGSIZE = 1000000
        autosub.LOGNUM = 1

    if cfg.has_section('webserver'):
        if cfg.has_option('webserver', 'webserverip') and cfg.has_option('webserver', 'webserverport'):
            autosub.WEBSERVERIP = cfg.get('webserver', 'webserverip')
            autosub.WEBSERVERPORT = int(cfg.get('webserver', 'webserverport'))
        else:
            print "Config ERROR: Webserver IP and port are required! Now setting the default values (127.0.0.1:8080)."
            autosub.WEBSERVERIP = "127.0.0.1"
            autosub.WEBSERVERPORT = 8080
        if cfg.has_option('webserver', 'username') and cfg.has_option('webserver', 'password'):
            autosub.USERNAME = cfg.get('webserver', 'username')
            autosub.PASSWORD = cfg.get('webserver', 'password')
        elif cfg.has_option('webserver', 'username') or cfg.has_option('webserver', 'password'):
            print "Config ERROR: Both username and password are required! Now starting without authentication!"
    else:
        print "Config ERROR: The webserver section is required! Now setting the default values (127.0.0.1:8080)."
        print "Config WARNING: The webserver is started without authentication!"
        autosub.WEBSERVERIP = '127.0.0.1'
        autosub.WEBSERVERPORT = 8080

    if cfg.has_section('skipshow'):
        # Try to read skipshow section in the config
        autosub.SKIPSHOW = dict(cfg.items('skipshow'))
        # The following 4 lines convert the skipshow to uppercase. And also convert the variables to a list
        autosub.SKIPSHOWUPPER = {}
        for x in autosub.SKIPSHOW:
            autosub.SKIPSHOWUPPER[x.upper()] = autosub.SKIPSHOW[x].split(',')
    else:
        autosub.SKIPSHOW = {}

    if cfg.has_section('namemapping'):
        autosub.USERNAMEMAPPING = dict(cfg.items('namemapping'))
        autosub.USERNAMEMAPPINGUPPER = {}
        for x in autosub.USERNAMEMAPPING.keys():
            autosub.USERNAMEMAPPINGUPPER[x.upper()] = autosub.USERNAMEMAPPING[x]
    else:
        autosub.USERNAMEMAPPING = {}
        autosub.USERNAMEMAPPINGUPPER = {}

    if cfg.has_section('dev'):
        if cfg.has_option('dev', 'apikey'):
            autosub.APIKEY = cfg.get('dev', 'APIKEY')

    # If an option or section wasn't in the config file we add it
    if edited:
        with open(configfile, 'wb') as file:
            cfg.write(file)

    # Settings
    autosub.SHOWID_CACHE = {}

    # This dictionary maps local series names to BierDopje ID's
    # Example: namemapping = {"Castle":"12708"}
    autosub.NAMEMAPPING = {
            "Greys Anatomy": "3733",
            "Grey's Anatomy": "3733",
            "Csi Miami": "2187",
            "Mr Sunshine": "14224",
            "Spartacus Gods Of The Arena": "14848",
            "Spartacus Blood And Sand": "13942",
            "Hawaii Five 0": "14211",
            "Hawaii Five-0": "14211",
            "Hawaii Five 0 2010": "14211",
            "Castle (2009)": "12708",
            "Against the Wall": "15522",
            "Body of Proof": "14420",
            "Rizzoli And Isles": "14175",
            "Melissa And Joey": "14470",
            "Charlies Angels 2011": "15205",
            "Femme Fatales": "15519",
            "Free Agents Us": "15256",
            "Merlin 2008": "5985",
            "Shameless Us": "14718",
            "Prime Suspect Us": "15249",
            "Harrys Law": "14489",
            "Man Up": "15209",
            "The La Complex": "15953",
            "Spartacus": "13942",
            "The Kennedys": "15067",
            "Last Man Standing Us": "15201",
            "Up All Night 2011": "15261",
            "Are You There Chelsea": "15259",
            "Touch": "15761",
            "Ncis Los Angeles": "12994",
            "Mike and Molly": "14258"
    }

    autosub.NAMEMAPPINGUPPER = {}
    for x in autosub.NAMEMAPPING.keys():
        autosub.NAMEMAPPINGUPPER[x.upper()] = autosub.NAMEMAPPING[x]

    autosub.LASTESTDOWNLOAD = []


def SaveToConfig(section=None, variable=None, value=None):
    """
    Add a variable and value to section in the config file.
    
    Keyword arguments:
    section -- Section to with the variable - value pair will be added
    variable -- Option that will be added to the config file
    value -- Value of the variable that will be added
    """
    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)

    if cfg.has_section(section):
        cfg.set(section, variable, value)
        edited = True
    else:
        cfg.add_section(section)
        cfg.set(section, variable, value)
        edited = True

    if edited:
        with open(autosub.CONFIGFILE, 'wb') as file:
            cfg.write(file)


def applynameMapping():
    """
    Read namemapping in the config file.
    """
    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)
    autosub.SHOWID_CACHE = {}
    autosub.USERNAMEMAPPING = dict(cfg.items('namemapping'))
    autosub.USERNAMEMAPPINGUPPER = {}
    for x in autosub.USERNAMEMAPPING.keys():
        autosub.USERNAMEMAPPINGUPPER[x.upper()] = autosub.USERNAMEMAPPING[x]


def applyskipShow():
    """
    Read skipshow in the config file.
    """
    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)
    autosub.SKIPSHOW = dict(cfg.items('skipshow'))
    autosub.SKIPSHOWUPPER = {}
    for x in autosub.SKIPSHOW:
        autosub.SKIPSHOWUPPER[x.upper()] = autosub.SKIPSHOW[x].split(',')


def applyAllSettings():
    """
    Add namemapping and skipshow to the config file
    """
    applynameMapping()
    applyskipShow()
