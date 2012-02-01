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

def ReadConfig(configfile):
		# Read config file
	autosub.ROOTPATH = os.getcwd()
	autosub.FALLBACKTOENG = True
	autosub.SUBENG = "en"
	autosub.LOGFILE = "AutoSubService.log"
	edited=False
		
	cfg = SafeConfigParser()
	cfg.read(configfile)
	
	if cfg.has_section('config'):
		if cfg.has_option('config', 'path'):
			autosub.APIKEY = cfg.get('config','path')
	
	try:
		dict(cfg.items('config'))
	except:
		cfg.add_section('config')
		edited=True
	try:	
		autosub.ROOTPATH=cfg.get("config", "ROOTPATH")
	except:
		cfg.set("config","ROOTPATH",autosub.ROOTPATH)
		edited=True
	try:
		autosub.FALLBACKTOENG=cfg.getboolean("config", "FALLBACKTOENG")
	except:
		cfg.set("config","FALLBACKTOENG",str(autosub.FALLBACKTOENG))
		edited=True
	try:	
		autosub.SUBENG=cfg.get("config", "SUBENG")
	except:
		cfg.set("config","SUBENG",autosub.SUBENG)
		edited=True
	try:
		autosub.SUBNL=cfg.get("config","SUBNL")
	except:
		autosub.SUBNL=""
	
	try:
		autosub.WORKDIR=cfg.get("config","workdir")
	except:
		autosub.WORKDIR=None
	
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
		autosub.LOGSIZE=100000
	
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
	for x in autosub.SKIPSHOWUPPER:
		autosub.SKIPSHOWUPPER[x.upper()] = autosub.SKIPSHOWUPPER[x].split(',')
	
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
			"Are You There Chelsea":"15259"
	}
	autosub.USERNAMEMAPPINGUPPER = {}
	for x in autosub.USERNAMEMAPPING.keys():
		autosub.USERNAMEMAPPINGUPPER[x.upper()] = autosub.USERNAMEMAPPING[x]
	print autosub.USERNAMEMAPPING
	autosub.NAMEMAPPINGUPPER = {}
	for x in autosub.NAMEMAPPING.keys():
		autosub.NAMEMAPPINGUPPER[x.upper()] = autosub.NAMEMAPPING[x]

