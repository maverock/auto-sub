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
	scandisk = autosub.Scheduler.Scheduler(autosub.scanDisk.scanDisk(),autosub.SCHEDULERSCANDISK,True,"LOCALDISK")
	scandisk.thread.start()

	checkrss = autosub.Scheduler.Scheduler(autosub.checkRss.checkRss(),autosub.SCHEDULERCHECKRSS,True,"CHECKRSS")
	checkrss.thread.start()

	checksub = autosub.Scheduler.Scheduler(autosub.checkSub.checkSub(),autosub.SCHEDULERCHECKSUB,True,"CHECKSUB")
	checksub.thread.start()

	downloadSubs = autosub.Scheduler.Scheduler(autosub.downloadSubs.downloadSubs(),autosub.SCHEDULERDOWNLOADSUBS,True,"DOWNLOADSUBS")
	downloadSubs.thread.start()
	
def signal_handler(signum, frame):
	log.debug("AutoSub: got signal. Shutting down")
	os._exit(0)