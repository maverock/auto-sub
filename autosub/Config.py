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
# TODO: Auto restart if needed after saving config
# TODO: Make the config page pretty again
# TODO: Make user re-enter password and compare 'em to rule out typing errors
# TODO: Code cleanup?


def ReadConfig(configfile):
    """
    Read the config file and set all the variables.
    """

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
            autosub.SCHEDULERCHECKSUB = 86400  # Run every 8 hours

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

        if cfg.has_option("config", "rootpath"):
            autosub.ROOTPATH = cfg.get("config", "rootpath")
        else:
            print "Config ERROR: Variable ROOTPATH is missing. This is required! Using current working directory instead."
            autosub.ROOTPATH = os.getcwd()

        if cfg.has_option("config", "fallbacktoeng"):
            autosub.FALLBACKTOENG = cfg.getboolean("config", "fallbacktoeng")
        else:
            autosub.FALLBACKTOENG = True

        if cfg.has_option("config", "subeng"):
            autosub.SUBENG = cfg.get("config", "subeng")
        else:
            autosub.SUBENG = 'en'

        if cfg.has_option("config", "subnl"):
            autosub.SUBNL = cfg.get("config", "subnl")
        else:
            autosub.SUBNL = ""

        if cfg.has_option("config", "workdir"):
            autosub.PATH = cfg.get("config", "workdir")
            print "Config WARNING: Workdir is an old variable. Replace it with 'path'."

        if cfg.has_option("config", "logfile"):
            autosub.LOGFILE = cfg.get("config", "logfile")
        else:
            print "Config ERROR: Variable LOGFILE is missing. This is required! Using 'AutoSubService.log' instead."
            autosub.LOGFILE = "AutoSubService.log"

        if cfg.has_option("config", "postprocesscmd"):
            autosub.POSTPROCESSCMD = cfg.get("config", "postprocesscmd")

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

    if cfg.has_section('logfile'):
        if cfg.has_option("logfile", "loglevel"):
            autosub.LOGLEVEL = cfg.get("logfile", "loglevel")
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

        if cfg.has_option("logfile", "logsize"):
            autosub.LOGSIZE = int(cfg.get("logfile", "logsize"))
        else:
            autosub.LOGSIZE = 1000000

        if cfg.has_option("logfile", "lognum"):
            autosub.LOGNUM = int(cfg.get("logfile", "lognum"))
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
            print "Config ERROR: Webserver IP and port are required! Now setting the default values (0.0.0.0:8083)."
            autosub.WEBSERVERIP = "0.0.0.0"
            autosub.WEBSERVERPORT = 8083
        if cfg.has_option('webserver', 'username') and cfg.has_option('webserver', 'password'):
            autosub.USERNAME = cfg.get('webserver', 'username')
            autosub.PASSWORD = cfg.get('webserver', 'password')
        elif cfg.has_option('webserver', 'username') or cfg.has_option('webserver', 'password'):
            print "Config ERROR: Both username and password are required! Now starting without authentication!"
    else:
        print "Config ERROR: The webserver section is required! Now setting the default values (0.0.0.0:8083)."
        print "Config WARNING: The webserver is started without authentication!"
        autosub.WEBSERVERIP = '0.0.0.0'
        autosub.WEBSERVERPORT = 8083

    if cfg.has_section('skipshow'):
        # Try to read skipshow section in the config
        autosub.SKIPSHOW = dict(cfg.items('skipshow'))
        # The following 4 lines convert the skipshow to uppercase. And also convert the variables to a list
        autosub.SKIPSHOWUPPER = {}
        for x in autosub.SKIPSHOW:
            autosub.SKIPSHOWUPPER[x.upper()] = autosub.SKIPSHOW[x].split(',')
    else:
        autosub.SKIPSHOW = {}
        autosub.SKIPSHOWUPPER = {}

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
            autosub.APIKEY = cfg.get('dev', 'apikey')

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
    if cfg.has_section("namemapping"):
        autosub.USERNAMEMAPPING = dict(cfg.items('namemapping'))
    else:
        autosub.USERNAMEMAPPING = {}
    autosub.USERNAMEMAPPINGUPPER = {}
    for x in autosub.USERNAMEMAPPING.keys():
        autosub.USERNAMEMAPPINGUPPER[x.upper()] = autosub.USERNAMEMAPPING[x]


def applyskipShow():
    """
    Read skipshow in the config file.
    """
    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)
    if cfg.has_section('skipshow'):
        autosub.SKIPSHOW = dict(cfg.items('skipshow'))
    else:
        autosub.SKIPSHOW = {}
    autosub.SKIPSHOWUPPER = {}
    for x in autosub.SKIPSHOW:
        autosub.SKIPSHOWUPPER[x.upper()] = autosub.SKIPSHOW[x].split(',')


def applyAllSettings():
    """
    Read namemapping and skipshow from the config file.
    """
    applynameMapping()
    applyskipShow()


def displaySkipshow():
    """
    Return a string containing all info from skipshow.
    After each shows skip info an '\n' is added to create multiple rows
    in a textarea.
    """
    s = ""
    for x in autosub.SKIPSHOW:
        s += x + " = " + str(autosub.SKIPSHOW[x]) + "\n"
    return s


def displayNamemapping():
    """
    Return a string containing all info from user namemapping.
    After each shows namemapping an '\n' is added to create multiple rows
    in a textarea.
    """
    s = ""
    for x in autosub.USERNAMEMAPPING:
        s += x + " = " + str(autosub.USERNAMEMAPPING[x]) + "\n"
    return s


def stringToDict(items=None):
    """
    Return a correct dict from a string
    """
    items = items.split('\r\n')
    returnitems = []

    for item in items:
        if item:
            showinfo = []
            for x in item.split('='):
                if x[-1:] == ' ':
                    x = x[:-1]
                elif x[:1] == ' ':
                    x = x[1:]
                showinfo.append(x)
            showinfo = tuple(showinfo)
            returnitems.append(showinfo)
    returnitems = dict(returnitems)
    return returnitems


def saveConfigSection():
    """
    Save stuff
    """
    section = 'config'

    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)

    if not cfg.has_section(section):
        cfg.add_section(section)

    cfg.set(section, "path", autosub.PATH)
    cfg.set(section, "downloadeng", autosub.DOWNLOADENG)
    cfg.set(section, "minmatchscore", str(autosub.MINMATCHSCORE))
    cfg.set(section, "minmatchscorerss", str(autosub.MINMATCHSCORERSS))
    cfg.set(section, "scandisk", str(autosub.SCHEDULERSCANDISK))
    cfg.set(section, "checksub", str(autosub.SCHEDULERCHECKSUB))
    cfg.set(section, "checkrss", str(autosub.SCHEDULERCHECKRSS))
    cfg.set(section, "downloadsubs", str(autosub.SCHEDULERDOWNLOADSUBS))
    cfg.set(section, "rootpath", autosub.ROOTPATH)
    cfg.set(section, "fallbacktoeng", autosub.FALLBACKTOENG)
    cfg.set(section, "subeng", autosub.SUBENG)
    cfg.set(section, "subnl", autosub.SUBNL)
    cfg.set(section, "logfile", autosub.LOGFILE)
    cfg.set(section, "postprocesscmd", autosub.POSTPROCESSCMD)

    with open(autosub.CONFIGFILE, 'wb') as file:
        cfg.write(file)


def saveLogfileSection():
    """
    Save stuff
    """
    section = 'logfile'

    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)

    if not cfg.has_section(section):
        cfg.add_section(section)

    cfg.set(section, "loglevel", logging.getLevelName(int(autosub.LOGLEVEL)).lower())
    cfg.set(section, "loglevelconsole", logging.getLevelName(int(autosub.LOGLEVELCONSOLE)).lower())
    cfg.set(section, "logsize", str(autosub.LOGSIZE))
    cfg.set(section, "lognum", str(autosub.LOGNUM))

    with open(autosub.CONFIGFILE, 'wb') as file:
        cfg.write(file)


def saveWebserverSection():
    """
    Save stuff
    """
    section = 'webserver'

    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)

    if not cfg.has_section(section):
        cfg.add_section(section)

    cfg.set(section, "webserverip", str(autosub.WEBSERVERIP))
    cfg.set(section, 'webserverport', str(autosub.WEBSERVERPORT))
    cfg.set(section, "username", autosub.USERNAME)
    cfg.set(section, "password", autosub.PASSWORD)

    with open(autosub.CONFIGFILE, 'wb') as file:
        cfg.write(file)


def saveSkipshowSection():
    """
    Save stuff
    """
    section = 'skipshow'

    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)

    if not cfg.has_section(section):
        cfg.add_section(section)

    for x in autosub.SKIPSHOW:
        SaveToConfig('skipshow', x, autosub.SKIPSHOW[x])

    # Set all skipshow stuff correct
    applyskipShow()


def saveUsernamemappingSection():
    """
    Save stuff
    """
    section = 'namemapping'

    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)

    if not cfg.has_section(section):
        cfg.add_section(section)

    for x in autosub.USERNAMEMAPPING:
        SaveToConfig('namemapping', x, autosub.USERNAMEMAPPING[x])

    # Set all namemapping stuff correct
    applynameMapping()


def checkForRestart():
    """
    Check if internal variables are different from the config file.
    Only check the variables the require a restart to take effect
    """
    cfg = SafeConfigParser()
    cfg.read(autosub.CONFIGFILE)

    # Set the default values
    schedulerscandisk = 3600
    schedulerchecksub = 28800
    schedulercheckrss = 900
    schedulerdownloadsubs = 1
    loglevel = logging.INFO
    loglevelconsole = logging.ERROR
    logsize = 1000000
    lognum = 1
    webserverip = '127.0.0.1'
    webserverport = 8080
    username = ''
    password = ''

    # Check if an option excists in the config file, if so replace the default value
    if cfg.has_section('config'):
        if cfg.has_option('config', 'scandisk'):
            schedulerscandisk = int(cfg.get('config', 'scandisk'))

        if cfg.has_option('config', 'checksub'):
            schedulerchecksub = int(cfg.get('config', 'checksub'))

        if cfg.has_option('config', 'checkrss'):
            schedulercheckrss = int(cfg.get('config', 'checkrss'))

        if cfg.has_option('config', 'downloadsubs'):
            schedulerdownloadsubs = int(cfg.get('config', 'downloadsubs'))

    if cfg.has_option("config", "logfile"):
        logfile = cfg.get("config", "logfile")

    if cfg.has_section('logfile'):
        if cfg.has_option("logfile", "loglevel"):
            loglevel = cfg.get("logfile", "loglevel")
            if loglevel.lower() == 'error':
                loglevel = logging.ERROR
            elif loglevel.lower() == "warning":
                loglevel = logging.WARNING
            elif loglevel.lower() == "debug":
                loglevel = logging.DEBUG
            elif loglevel.lower() == "info":
                loglevel = logging.INFO
            elif loglevel.lower() == "critical":
                loglevel = logging.CRITICAL

        if cfg.has_option("logfile", "loglevelconsole"):
            loglevelconsole = cfg.get("logfile", "loglevelconsole")
            if loglevelconsole.lower() == 'error':
                loglevelconsole = logging.ERROR
            elif loglevelconsole.lower() == "warning":
                loglevelconsole = logging.WARNING
            elif loglevelconsole.lower() == "debug":
                loglevelconsole = logging.DEBUG
            elif loglevelconsole.lower() == "info":
                loglevelconsole = logging.INFO
            elif loglevelconsole.lower() == "critical":
                loglevelconsole = logging.CRITICAL

        if cfg.has_option("logfile", "logsize"):
            logsize = int(cfg.get("logfile", "logsize"))

        if cfg.has_option("logfile", "lognum"):
            lognum = int(cfg.get("logfile", "lognum"))

    if cfg.has_section('webserver'):
        if cfg.has_option('webserver', 'webserverip') and cfg.has_option('webserver', 'webserverport'):
            webserverip = cfg.get('webserver', 'webserverip')
            webserverport = int(cfg.get('webserver', 'webserverport'))
        if cfg.has_option('webserver', 'username') and cfg.has_option('webserver', 'password'):
            username = cfg.get('webserver', 'username')
            password = cfg.get('webserver', 'password')

    # Now compare the values, if one differs a restart is required.
    if schedulerscandisk != autosub.SCHEDULERSCANDISK or schedulerchecksub != autosub.SCHEDULERCHECKSUB or schedulercheckrss != autosub.SCHEDULERCHECKRSS or schedulerdownloadsubs != autosub.SCHEDULERDOWNLOADSUBS or loglevel != autosub.LOGLEVEL or loglevelconsole != autosub.LOGLEVELCONSOLE or logsize != autosub.LOGSIZE or lognum != autosub.LOGNUM or webserverip != autosub.WEBSERVERIP or webserverport != autosub.WEBSERVERPORT or username != autosub.USERNAME or password != autosub.PASSWORD:
        return True
    else:
        return False


def WriteConfig():
    """
    Save all settings to the config file.
    Return message about the write.
    """
    # Read config file
    cfg = SafeConfigParser()
    try:
        # A config file is set so we use this to add the settings
        cfg.read(autosub.CONFIGFILE)
    except:
        # No config file so we create one in autosub.PATH
        autosub.CONFIGFILE = "config.properties"
        cfg.read(autosub.CONFIGFILE)

    # Before we save everything to the config file we need to test if
    # the app needs to be restarted for all changes to take effect, like
    # logfile and webserver sections
    restart = checkForRestart()
    
    saveConfigSection()
    saveLogfileSection()
    saveWebserverSection()
    saveSkipshowSection()
    saveUsernamemappingSection()

    if restart:
        # This needs to be replaced by a restart thingy, until then, just re-read the config and tell the users to do a manual restart
        ReadConfig(autosub.CONFIGFILE)
        return "Config saved. A manual restart is needed for all changes to take effect. Auto restart will be implemented soon!<br><a href='/config'>Return</a>"
    else:
        # For some reason the needs to be read again, otherwise all pages get an error
        ReadConfig(autosub.CONFIGFILE)
        return "Config saved.<br><a href='/config'>Return</a>"
