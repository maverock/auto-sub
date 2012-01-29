# Autosub Config.py - http://code.google.com/p/auto-sub/
#
# The Autosub config Module
# 

#python 2.5 support
from __future__ import with_statement 

import urllib
import urllib2
import os
import re
import logging

from ConfigParser import SafeConfigParser

# Autosub specific modules

# Settings -----------------------------------------------------------------------------------------------------------------------------------------
# Location of the configuration file:
#configfile = "config.properties"
# Set the logger
log = logging.getLogger('thelogger')
#/Settings -----------------------------------------------------------------------------------------------------------------------------------------

class Properties():
	rootpath=None
	fallbackToEng=None
	subeng=None
	logfile=None
	subnl=None
	loglevel=None
	loglevelconsole=None
	logsize=None
	lognum=None
	skipshow=None
	skipshowupper=None
	usernamemapping=None
	postprocesscmd=None
	namemapping=None
	usernamemappingupper=None
	namemappingupper=None
	showid_cache=None
	
def ReadConfig(configfile):
		# Read config file
	Properties.rootpath = os.getcwd()
	Properties.fallbackToEng = True
	Properties.subeng="en"
	Properties.logfile="AutoSubService.log"
	edited=False
		
	cfg = SafeConfigParser()
	cfg.read(configfile)

	try:
		dict(cfg.items('config'))
	except:
		cfg.add_section('config')
		edited=True
	try:	
		Properties.rootpath=cfg.get("config", "ROOTPATH")
	except:
		cfg.set("config","ROOTPATH",Properties.rootpath)
		edited=True
	try:
		Properties.fallbackToEng=cfg.getboolean("config", "FALLBACKTOENG")
	except:
		cfg.set("config","FALLBACKTOENG",str(Properties.fallbackToEng))
		edited=True
	try:	
		Properties.subeng=cfg.get("config", "SUBENG")
	except:
		cfg.set("config","SUBENG",Properties.subeng)
		edited=True
	try:
		Properties.subnl=cfg.get("config","SUBNL")
	except:
		Properties.subnl=""
	
	try:
		Properties.workdir=cfg.get("config","workdir")
	except:
		Properties.workdir=""
	
	try:
		Properties.logfile= cfg.get("config", "LOGFILE")
	except:
		cfg.set("config","LOGFILE",Properties.logfile) 
		edited=True
	
	try:
		Properties.loglevel=cfg.get("logfile","LOGLEVEL")
		if Properties.loglevel.lower()=='error':
			Properties.loglevel=logging.ERROR
		elif Properties.loglevel.lower()=="warning":
			Properties.loglevel=logging.WARNING
		elif Properties.loglevel.lower()=="debug":
			Properties.loglevel=logging.DEBUG
		elif Properties.loglevel.lower()=="info":
			Properties.loglevel=logging.WARNING
		elif Properties.loglevel.lower()=="critical":
			Properties.loglevel=logging.CRITICAL
	except:
		Properties.loglevel=logging.ERROR
	
	try:
		Properties.loglevelconsole=cfg.get("logfile","loglevelconsole")
		if Properties.loglevelconsole.lower()=='error':
			Properties.loglevelconsole=logging.ERROR
		elif Properties.loglevelconsole.lower()=="warning":
			Properties.loglevelconsole=logging.WARNING
		elif Properties.loglevelconsole.lower()=="debug":
			Properties.loglevelconsole=logging.DEBUG
		elif Properties.loglevelconsole.lower()=="info":
			Properties.loglevelconsole=logging.WARNING
		elif Properties.loglevelconsole.lower()=="critical":
			Properties.loglevelconsole=logging.CRITICAL
	except:
		Properties.loglevelconsole=logging.INFO
	
	try:
		Properties.logsize=int(cfg.get("logfile","LOGSIZE"))
	except:
		Properties.logsize=100000
	
	try :
		Properties.lognum=int(cfg.get("logfile"),"LOGNUM")
	except:
		Properties.lognum=3
	
	Properties.skipshow={}
	
	try:
	# Try to read skipshow section in the config
		Properties.skipshow = dict(cfg.items('skipshow'))
	except:
		cfg.add_section('skipshow')
		edited=True  

	# Try to read skipshow section in the config
	Properties.skipshow = dict(cfg.items('skipshow'))

	# The following 4 lines convert the skipshow to uppercase. And also convert the variables to a list 
	Properties.skipshowupper = {}
	for x in Properties.skipshow:
		Properties.skipshowupper[x.upper()] = Properties.skipshow[x].split(',')
	
	try:
		Properties.usernamemapping = dict(cfg.items('namemapping'))
	except:
		cfg.add_section('namemapping')
		edited=True
	Properties.usernamemapping = dict(cfg.items('namemapping'))
	
	try:
		Properties.postprocesscmd = cfg.get("config", "POSTPROCESSCMD")
	except:
		Properties.postprocesscmd = False
		
	if edited:
		with open(configfile, 'wb') as file:
			cfg.write(file)
	
	# Settings
	Properties.showid_cache = {}

	# This dictionary maps local series names to BierDopje ID's
	# Example: namemapping = {"Castle":"12708"}
	Properties.namemapping = {
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
			"Are You There Chelsea":"15259"
	}
	Properties.usernamemappingupper = {}
	for x in Properties.usernamemapping.keys():
		Properties.usernamemappingupper[x.upper()] = Properties.usernamemapping[x]
		
	Properties.namemappingupper = {}
	for x in Properties.namemapping.keys():
		Properties.namemappingupper[x.upper()] = Properties.namemapping[x]


def nameMapping(showName):
	if showName.upper() in Properties.usernamemappingupper.keys():
		log.debug("nameMapping: found match in user's namemapping for %s" %showName)
		return Properties.usernamemappingupper[showName.upper()]
	elif showName.upper() in Properties.namemappingupper.keys():
		log.debug("nameMapping: found match for %s" %showName)
		return Properties.namemappingupper[showName.upper()]
		
def SkipShow(showName,season,episode):
	if showName.upper() in Properties.skipshowupper.keys():
		log.debug("SkipShow: Found %s in skipshow dictonary" %showName)
		for seasontmp in Properties.skipshowupper[showName.upper()]:
			if seasontmp == '0':
				log.debug("SkipShow: variable of %s is set to 0, skipping the complete Serie" %showName)
				return True
			elif int(seasontmp) == int(season):
				log.debug("SkipShow: Season matches variable of %s, skipping season" %showName)
				return True	
