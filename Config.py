# Autosub Config.py - http://code.google.com/p/auto-sub/
#
# The Autosub config Module
# 

import urllib
import urllib2
import os
import re
import logging

from ConfigParser import SafeConfigParser

# Autosub specific modules

# Settings -----------------------------------------------------------------------------------------------------------------------------------------
# Location of the configuration file:
configfile = "config.properties"
# Set the logger
log = logging.getLogger('thelogger')
#/Settings -----------------------------------------------------------------------------------------------------------------------------------------


class Properties():
	
	# Read config file
	rootpath = os.getcwd()
	fallbackToEng = True
	subeng="en"
	logfile="AutoSubService.log"
	edited=False
		
	cfg = SafeConfigParser()
	cfg.read(configfile)

	try:
		dict(cfg.items('config'))
	except:
		cfg.add_section('config')
		edited=True
	try:    
		rootpath=cfg.get("config", "ROOTPATH")
	except:
		cfg.set("config","ROOTPATH",rootpath)
		edited=True
	try:
		fallbackToEng=cfg.getboolean("config", "FALLBACKTOENG")
	except:
		cfg.set("config","FALLBACKTOENG",str(fallbackToEng))
		edited=True
	try:    
		subeng=cfg.get("config", "SUBENG")
	except:
		cfg.set("config","SUBENG",subeng)
		edited=True
	try:
		logfile= cfg.get("config", "LOGFILE")
	except:
		cfg.set("config","LOGFILE",logfile) 
		edited=True
	
	skipshow={}
	
	try:
	# Try to read skipshow section in the config
		skipshow = dict(cfg.items('skipshow'))
	except:
		cfg.add_section('skipshow')
		edited=True  

	# Try to read skipshow section in the config
	skipshow = dict(cfg.items('skipshow'))

	# The following 4 lines convert the skipshow to uppercase. And also convert the variables to a list 
	skipshowupper = {}
	for x in skipshow:
		skipshowupper[x.upper()] = skipshow[x].split(',')
	
	try:
		usernamemapping = dict(cfg.items('namemapping'))
	except:
		cfg.add_section('namemapping')
		edited=True
	
	usernamemapping = dict(cfg.items('namemapping'))
	
	if edited:
		with open(configfile, 'wb') as file:
			cfg.write(file)
	
	# Settings
	showid_cache = {}

	# This dictionary maps local series names to BierDopje ID's
	# Example: namemapping = {"Castle":"12708"}
	namemapping = {
			"Greys Anatomy" : "3733",
			"Grey's Anatomy" : "3733",
			"Csi Miami" : "2187",
			"Mr Sunshine":"14224",
			"Spartacus Gods Of The Arena":"14848",
			"Spartacus Blood And Sand":"13942",
			"Hawaii Five 0":"14211",
			"Hawaii Five-0":"14211",
			"Castle (2009)":"12708",
			"Against the Wall":"15522",
			"Body of Proof":"14420"
	}
	usernamemappingupper = {}
	for x in usernamemapping.keys():
		usernamemappingupper[x.upper()] = usernamemapping[x]
		
	namemappingupper = {}
	for x in namemapping.keys():
		namemappingupper[x.upper()] = namemapping[x]

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