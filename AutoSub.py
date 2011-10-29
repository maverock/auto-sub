# AutoSub - http://code.google.com/p/auto-sub/
# v6.xx
#
# What does it do?
# Scans a directory and checks if the TV Episode has a ".srt" file
# If not it will attempt to download the dutch version from bierdopje.com

import logging.handlers
import time
import sys
import getopt


# Autosub specific modules:
import Bierdopje
import Helpers
import LocalDisk
import Config

# !!!! DO NOT MODIFY BEYOND THIS LINE !!!! ---------------------------------------------------------------------------------------------------------


help_message = '''
Usage:
	-h (--help)	Prints this message
	

Example:
	python AutoSub.py
'''

	
class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg
	
def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args= getopt.getopt(argv[1:], "h", ["help"])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		for option, value in opts:
			if option in ("-h", "--help"):
				raise Usage(help_message)
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2
	
	# wantedQueue carries a list of Episodes which do not have a SRT yet and need to be checked
	# data: title, season, episode, quality, source*, releaseGrp*, originalFileLocationOnDisk (items with * are optional)
	wantedQueue = []
	# toDownloadQueue carries a list of Episodes which are confirmed on the Source and need to be downloaded
	# data: title, season, episode, quality, source*, releaseGrp*, downloadLink, originalFileLocationOnDisk, destinationFileLocationOnDisk (items with * are optional)
	toDownloadQueue = []
	
	#load configuration
	config = Config.Properties()
	#config.load()
	
	LOGLEVEL=logging.DEBUG
	LOGSIZE= 100000000
	LOGNUM = 10

	# initialize logging
	# A log directory has to be created below the start directory
	log = logging.getLogger("thelogger")
	log.setLevel(LOGLEVEL)

	log_script = logging.handlers.RotatingFileHandler(config.logfile, 'a', LOGSIZE, LOGNUM)
	log_script_formatter=logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
	log_script.setFormatter(log_script_formatter)
	log_script.setLevel(LOGLEVEL)
	log.addHandler(log_script)

	#CONSOLE log handler
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	# set a format which is simpler for console use
	formatter = logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
	console.setFormatter(formatter)
	log.addHandler(console)
	
	
	#initial scan&check
	wantedQueue = LocalDisk.scanDir(config.rootpath)
	wantedQueue, toDownloadQueue = Bierdopje.checkSub(wantedQueue, toDownloadQueue)
	wantedQueue, toDownloadQueue = Bierdopje.checkRSS(wantedQueue, toDownloadQueue)
	
	# take timestamps
	ts_scanDir = time.time()
	ts_checkSub = time.time()
	ts_checkRSS = time.time()
	
	while True:
		#every tick check for length if not 0: do Download
		if len(toDownloadQueue) > 0:
			log.info("main: Found %s items in toDownloadQueue, running downloadSubs" %(len(toDownloadQueue)))
			toDownloadQueue = LocalDisk.downloadSubs(toDownloadQueue)
		
		#once every hour
		if time.time() - ts_scanDir > 3600:
			log.info("main: Haven't run scanDir for %s minutes, running scanDir" %(round((time.time() - ts_scanDir)/60)))
			wantedQueue = LocalDisk.scanDir(config.rootpath)
			ts_scanDir = time.time()
		
		#once every 8 hours
		if time.time() - ts_checkSub > 28800:
			log.info("main: Haven't run checkSub for %s minutes, running checkSub" %(round((time.time() - ts_checkSub)/60)))
			wantedQueue, toDownloadQueue = Bierdopje.checkSub(wantedQueue, toDownloadQueue)
			ts_checkSub = time.time()
		
		#once every 5 minutes
		if time.time() - ts_checkRSS > 300: 
			log.info("main: Haven't run checkRSS for %s minutes, running checkRSS" %(round((time.time() - ts_checkRSS)/60)))
			wantedQueue, toDownloadQueue = Bierdopje.checkRSS(wantedQueue, toDownloadQueue)
			ts_checkRSS = time.time()
	
		log.info("main: wantedQueue #: %s - toDownloadQueue #: %s" %(len(wantedQueue),len(toDownloadQueue)))
		#tick = set smallest timediff required
		time.sleep(300)

if __name__ == "__main__":
	sys.exit(main())
