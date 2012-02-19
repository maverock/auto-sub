# Autosub Config.py - http://code.google.com/p/auto-sub/
#
# The Autosub config Module
# 

#python 2.5 support
from __future__ import with_statement 

import os
import logging

from ConfigParser import SafeConfigParser

import autosub

# Autosub specific modules

# Settings -----------------------------------------------------------------------------------------------------------------------------------------
# Location of the configuration file:
#configfile = "config.properties"
# Set the logger
log = logging.getLogger('thelogger')
#/Settings -----------------------------------------------------------------------------------------------------------------------------------------

# TODO: Complete rewrite this function, remove try and replace with if statements if cfg.has_section etc.
# TODO: Webserver config, basic are done. CherryPy logging still needs a file only

def ReadConfig(configfile):
	# Read config file
	autosub.ROOTPATH = os.getcwd()
	autosub.FALLBACKTOENG = True
	autosub.SUBENG = "en"
	autosub.LOGFILE = "AutoSubService.log"
	edited=False
		
	cfg = SafeConfigParser()
	cfg.read(configfile)
	
	if cfg.has_section('webserver'):
		if cfg.has_option('webserver', 'webserverip') and cfg.has_option('webserver', 'webserverport'):
			autosub.WEBSERVERIP = cfg.get('webserver', 'webserverip')
			autosub.WEBSERVERPORT = int(cfg.get('webserver', 'webserverport'))
		if cfg.has_option('webserver', 'username') and cfg.has_option('webserver', 'password'):
			autosub.USERNAME = cfg.get('webserver', 'username')
			autosub.PASSWORD = cfg.get('webserver', 'password')
	else:
		cfg.add_section('webserver')
		cfg.set("webserver","webserverip",'127.0.0.1')
		cfg.set('webserver','webserverport','8080')
		edited = True
		autosub.WEBSERVERIP = '127.0.0.1'
		autosub.WEBSERVERPORT = 8080
	
	try:
		dict(cfg.items('config'))
	except:
		cfg.add_section('config')
		edited=True
	
	if cfg.has_section('config'):
		if cfg.has_option('config', 'path'):
			autosub.PATH = cfg.get('config','path')
		else:
			print "Config ERROR: Variable PATH is missing. This is required! Using current working directory instead"
			autosub.PATH = os.getcwd()
			cfg.set("config","PATH",autosub.PATH)
			edited=True
			
		if cfg.has_option('config', 'downloadeng'):
			autosub.DOWNLOADENG = cfg.getboolean('config','downloadeng')
		else:
			autosub.DOWNLOADENG = False

		if cfg.has_option('config','minmatchscore'):
			autosub.MINMATCHSCORE = int(cfg.get('config','minmatchscore'))
		else:
			autosub.MINMATCHSCORE = 0
		
		if cfg.has_option('config','minmatchscoreRSS'):
			autosub.MINMATCHSCORERSS = int(cfg.get('config','minmatchscorerss'))
		else:
			autosub.MINMATCHSCORERSS = 4
	
		if cfg.has_option('config','scandisk'):
			autosub.SCHEDULERSCANDISK = int(cfg.get('config','scandisk'))
		else:
			autosub.SCHEDULERSCANDISK=3600
			
		if cfg.has_option('config','checksub'):
			autosub.SCHEDULERCHECKSUB = int(cfg.get('config','checksub'))
			#CHECKSUB may only be runed 6 times a day, to prevent the API key from being banned
			#If you want new subtitles faster, you should decrease the CHECKRSS time
			if autosub.SCHEDULERCHECKSUB < 21600: 
				print "Config WARNING: checksub variable is lower then 21600! This is not allowed, this is to prevent our API-key from being banned"
				autosub.SCHEDULERCHECKSUB = 21600 #Run every 6 hours
		else:
			autosub.SCHEDULERCHECKSUB=28800 #Run every 8 hours
			
		if cfg.has_option('config','checkrss'):
			autosub.SCHEDULERCHECKRSS = int(cfg.get('config','checkrss'))
			#Because of the http timeout it is not recommened to set checkrss lower then 1 minute
			if autosub.SCHEDULERCHECKRSS < 60:
				print "Config WARNING: checkrss variable is lower then 60. Because of http timeout it is not recommended to set it below 60 seconds"
				autosub.SCHEDULERCHECKRSS = 60 #Run every minute
		else:
			autosub.SCHEDULERCHECKRSS=900 #Run every 15 minutes
		
		if cfg.has_option('config','downloadsubs'):
			autosub.SCHEDULERDOWNLOADSUBS= int(cfg.get('config','downloadsubs'))
		else:
			autosub.SCHEDULERDOWNLOADSUBS=1 #Run every second
		
	try:	
		autosub.ROOTPATH=cfg.get("config", "ROOTPATH")
	except:
		cfg.set("config","ROOTPATH",autosub.ROOTPATH)
		edited=True
	try:
		autosub.FALLBACKTOENG=cfg.getboolean("config", "FALLBACKTOENG")
	except:
		autosub.FALLBACKTOENG=True
		cfg.set("config","FALLBACKTOENG",str(autosub.FALLBACKTOENG))
	try:	
		autosub.SUBENG=cfg.get("config", "SUBENG")
	except:
		autosub.SUBENG='en'
		cfg.set("config","SUBENG",autosub.SUBENG)
	try:
		autosub.SUBNL=cfg.get("config","SUBNL")
	except:
		autosub.SUBNL=""
	
	try:
		autosub.PATH=cfg.get("config","workdir")
		print "Config WARNING: Workdir is an old variable. Replace it with 'path'"
	except:
		pass
	
	try:
		autosub.LOGFILE= cfg.get("config", "LOGFILE")
	except:
		cfg.set("config","LOGFILE",autosub.LOGFILE) 
		edited=True
	
	try:
		autosub.LOGLEVEL=cfg.get("logfile","LOGLEVEL")
		if autosub.LOGLEVEL.lower()=='error':
			autosub.LOGLEVEL=logging.ERROR
		elif autosub.LOGLEVEL.lower()=="warning":
			autosub.LOGLEVEL=logging.WARNING
		elif autosub.LOGLEVEL.lower()=="debug":
			autosub.LOGLEVEL=logging.DEBUG
		elif autosub.LOGLEVEL.lower()=="info":
			autosub.LOGLEVEL=logging.INFO
		elif autosub.LOGLEVEL.lower()=="critical":
			autosub.LOGLEVEL=logging.CRITICAL
	except:
		autosub.LOGLEVEL=logging.INFO
	
	try:
		autosub.LOGLEVELCONSOLE=cfg.get("logfile","loglevelconsole")
		if autosub.LOGLEVELCONSOLE.lower()=='error':
			autosub.LOGLEVELCONSOLE=logging.ERROR
		elif autosub.LOGLEVELCONSOLE.lower()=="warning":
			autosub.LOGLEVELCONSOLE=logging.WARNING
		elif autosub.LOGLEVELCONSOLE.lower()=="debug":
			autosub.LOGLEVELCONSOLE=logging.DEBUG
		elif autosub.LOGLEVELCONSOLE.lower()=="info":
			autosub.LOGLEVELCONSOLE=logging.INFO
		elif autosub.LOGLEVELCONSOLE.lower()=="critical":
			autosub.LOGLEVELCONSOLE=logging.CRITICAL
	except:
		autosub.LOGLEVELCONSOLE=logging.ERROR
	
	try:
		autosub.LOGSIZE=int(cfg.get("logfile","LOGSIZE"))
	except:
		autosub.LOGSIZE=1000000
	
	try :
		autosub.LOGNUM=int(cfg.get("logfile"),"LOGNUM")
	except:
		autosub.LOGNUM=3
	
	autosub.SKIPSHOW={}
	
	try:
	# Try to read skipshow section in the config
		autosub.SKIPSHOW = dict(cfg.items('skipshow'))
	except:
		cfg.add_section('skipshow')
		edited=True  

	# Try to read skipshow section in the config
	autosub.SKIPSHOW = dict(cfg.items('skipshow'))

	# The following 4 lines convert the skipshow to uppercase. And also convert the variables to a list 
	autosub.SKIPSHOWUPPER = {}
	for x in autosub.SKIPSHOW:
		autosub.SKIPSHOWUPPER[x.upper()] = autosub.SKIPSHOW[x].split(',')
	
	try:
		autosub.USERNAMEMAPPING = dict(cfg.items('namemapping'))
	except:
		cfg.add_section('namemapping')
		edited=True
	autosub.USERNAMEMAPPING = dict(cfg.items('namemapping'))
	
	try:
		autosub.POSTPROCESSCMD = cfg.get("config", "POSTPROCESSCMD")
	except:
		autosub.POSTPROCESSCMD = False
	
	if cfg.has_section('dev'):
		if cfg.has_option('dev', 'apikey'):
			autosub.APIKEY = cfg.get('dev','APIKEY')
		
	if edited:
		with open(configfile, 'wb') as file:
			cfg.write(file)
	
	# Settings
	autosub.SHOWID_CACHE = {}

	# This dictionary maps local series names to BierDopje ID's
	# Example: namemapping = {"Castle":"12708"}
	autosub.NAMEMAPPING = {
			"Greys Anatomy" : "3733",
			"Grey's Anatomy" : "3733",
			"Csi Miami" : "2187",
			"Mr Sunshine":"14224",
			"Spartacus Gods Of The Arena":"14848",
			"Spartacus Blood And Sand":"13942",
			"Hawaii Five 0":"14211",
			"Hawaii Five-0":"14211",
			"Hawaii Five 0 2010":"14211",
			"Castle (2009)":"12708",
			"Against the Wall":"15522",
			"Body of Proof":"14420",
			"Rizzoli And Isles":"14175",
			"Melissa And Joey":"14470",
			"Charlies Angels 2011":"15205",
			"Femme Fatales":"15519",
			"Free Agents Us":"15256",
			"Merlin 2008":"5985",
			"Shameless Us":"14718",
			"Prime Suspect Us":"15249",
			"Harrys Law":"14489",
			"Man Up":"15209",
			"The La Complex":"15953",
			"Spartacus":"13942",
			"The Kennedys":"15067",
			"Last Man Standing Us":"15201",
			"Up All Night 2011":"15261",
			"Are You There Chelsea":"15259",
			"Touch":"15761",
			"Ncis Los Angeles":"12994",
			"Mike and Molly":"14258"
	}
	autosub.USERNAMEMAPPINGUPPER = {}
	for x in autosub.USERNAMEMAPPING.keys():
		autosub.USERNAMEMAPPINGUPPER[x.upper()] = autosub.USERNAMEMAPPING[x]

	autosub.NAMEMAPPINGUPPER = {}
	for x in autosub.NAMEMAPPING.keys():
		autosub.NAMEMAPPINGUPPER[x.upper()] = autosub.NAMEMAPPING[x]

	autosub.LASTESTDOWNLOAD = []
	
def SaveToConfig(section=None,variable=None,value=None):
	cfg = SafeConfigParser()
	cfg.read(autosub.CONFIGFILE)
	
	if cfg.has_section(section):
		cfg.set(section,variable,value)
		edited=True
	else:
		cfg.add_section(section)
		cfg.set(section,variable,value)
		edited=True
			
	if edited:
		with open(autosub.CONFIGFILE, 'wb') as file:
			cfg.write(file)

def applynameMapping():
	cfg = SafeConfigParser()
	cfg.read(autosub.CONFIGFILE)
	autosub.SHOWID_CACHE = {}
	autosub.USERNAMEMAPPING = dict(cfg.items('namemapping'))
	autosub.USERNAMEMAPPINGUPPER = {}
	for x in autosub.USERNAMEMAPPING.keys():
		autosub.USERNAMEMAPPINGUPPER[x.upper()] = autosub.USERNAMEMAPPING[x]

def applyskipShow():
	cfg = SafeConfigParser()
	cfg.read(autosub.CONFIGFILE)
	autosub.SKIPSHOW = dict(cfg.items('skipshow'))
	autosub.SKIPSHOWUPPER = {}
	for x in autosub.SKIPSHOW:
		autosub.SKIPSHOWUPPER[x.upper()] = autosub.SKIPSHOW[x].split(',')

def applyAllSettings():
	applynameMapping()
	applyskipShow()
