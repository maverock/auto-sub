import autosub.Scheduler
import autosub.scanDisk
import autosub.checkRss
import autosub.checkSub
import autosub.downloadSubs

import logging
import os

# Settings
log = logging.getLogger('thelogger')

def start():
	log.info("AutoSub: Starting scanDisk thread")
	scandisk = autosub.Scheduler.Scheduler(autosub.scanDisk.scanDisk(),autosub.SCHEDULERSCANDISK,True,"LOCALDISK")
	scandisk.thread.start()
	log.info("AutoSub: scanDisk thread started")
	
	log.info("AutoSub: Starting checkRss thread")
	checkrss = autosub.Scheduler.Scheduler(autosub.checkRss.checkRss(),autosub.SCHEDULERCHECKRSS,True,"CHECKRSS")
	checkrss.thread.start()
	log.info("AutoSub: checkRss thread started")
	
	log.info("AutoSub: Starting checkSub thread")
	checksub = autosub.Scheduler.Scheduler(autosub.checkSub.checkSub(),autosub.SCHEDULERCHECKSUB,True,"CHECKSUB")
	checksub.thread.start()
	log.info("AutoSub: checkSub thread started")
	
	log.info("AutoSub: Starting downloadSubs thread")
	downloadSubs = autosub.Scheduler.Scheduler(autosub.downloadSubs.downloadSubs(),autosub.SCHEDULERDOWNLOADSUBS,True,"DOWNLOADSUBS")
	downloadSubs.thread.start()
	log.info("AutoSub: downloadSubs thread started")
	
def signal_handler(signum, frame):
	log.debug("AutoSub: got signal. Shutting down")
	os._exit(0)