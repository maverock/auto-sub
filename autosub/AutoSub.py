import autosub.Scheduler
import autosub.scanDisk
import autosub.checkRss
import autosub.checkSub
import autosub.downloadSubs
import autosub.WebServer

import logging
import os
import cherrypy
import sys

# Settings
log = logging.getLogger('thelogger')

def daemon():
	print "AutoSub: Starting as a daemon"
	try:
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError:
		sys.exit(1)
	
	os.chdir(autosub.PATH) 
	os.setsid() 
	os.umask(0)
	try:
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError:
		sys.exit(1)
	
	print "AutoSub: Disabling console output for daemon."
	
	cherrypy.log.screen = False
	sys.stdin.close()
	sys.stdout.flush()
	sys.stderr.flush()
	
def start():
	log.info("AutoSub: Starting scanDisk thread")
	autosub.SCANDISK = autosub.Scheduler.Scheduler(autosub.scanDisk.scanDisk(),autosub.SCHEDULERSCANDISK,True,"LOCALDISK")
	autosub.SCANDISK.thread.start()
	log.info("AutoSub: scanDisk thread started")
	
	log.info("AutoSub: Starting checkRss thread")
	autosub.CHECKRSS = autosub.Scheduler.Scheduler(autosub.checkRss.checkRss(),autosub.SCHEDULERCHECKRSS,True,"CHECKRSS")
	autosub.CHECKRSS.thread.start()
	log.info("AutoSub: checkRss thread started")
	
	log.info("AutoSub: Starting checkSub thread")
	autosub.CHECKSUB = autosub.Scheduler.Scheduler(autosub.checkSub.checkSub(),autosub.SCHEDULERCHECKSUB,True,"CHECKSUB")
	autosub.CHECKSUB.thread.start()
	log.info("AutoSub: checkSub thread started")
	
	log.info("AutoSub: Starting downloadSubs thread")
	autosub.DOWNLOADSUBS = autosub.Scheduler.Scheduler(autosub.downloadSubs.downloadSubs(),autosub.SCHEDULERDOWNLOADSUBS,True,"DOWNLOADSUBS")
	autosub.DOWNLOADSUBS.thread.start()
	log.info("AutoSub: downloadSubs thread started")
	
	cherrypy.config.update({'server.socket_host': autosub.WEBSERVERIP,
                        'server.socket_port': autosub.WEBSERVERPORT,
                       })
	
	cherrypy.tree.mount(autosub.WebServer.WebServerInit())
	log.info("AutoSub: Starting CherryPy webserver")
	
	# TODO: Let CherryPy log do another log file and not to screen
	# TODO: CherryPy settings, password protected etc...
	try:
		cherrypy.server.start()
	except:
		log.error("AutoSub: Could not start webserver. Exiting")
		os._exit(1)
		
	cherrypy.server.wait()

def stop():
	log.info("AutoSub: Stopping scanDisk thread")
	autosub.SCANDISK.stop = True
	autosub.SCANDISK.thread.join(10)
	
	log.info("AutoSub: Stopping checkRss thread")
	autosub.CHECKRSS.stop = True
	autosub.CHECKRSS.thread.join(10)
	
	log.info("AutoSub: Stopping checkSub thread")
	autosub.CHECKSUB.stop = True
	autosub.CHECKSUB.thread.join(10)
	
	log.info("AutoSub: Stopping downloadSubs thread")
	autosub.DOWNLOADSUBS.stop = True
	autosub.DOWNLOADSUBS.thread.join(10)
	
	cherrypy.engine.exit()
	
	os._exit(0)

def signal_handler(signum, frame):
	log.debug("AutoSub: got signal. Shutting down")
	os._exit(0)