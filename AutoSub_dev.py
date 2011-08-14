# AutoSub - http://code.google.com/p/auto-sub/
# v6.xx
#
# What does it do?
# Scans a directory and checks if the TV Episode has a ".srt" file
# If not it will attempt to download the dutch version from bierdopje.com

import logging.handlers
import urllib
import urllib2
import os
import time
import re
import sys
import getopt
from xml.dom import minidom


# Settings -----------------------------------------------------------------------------------------------------------------------------------------

# location of your TV Episodes
rootpath = "/mnt/nas1/content/TV"
# Set this to True if you also want the script to download the ENG version of the NLD is not available
# the english version will be named filename.eng.srt
fallbackToEng = True
# API key
apikey = "AFC34E2C2FE8B9F7"
# This dictionary maps local series names to BierDopje ID's
# Example: namemapping = {"Castle":"12708"}
namemapping = {}
# This dictionary can be use to skip shows or seasons from being downloaded. The seasons should be defined as lists
# Example: skipshow = {'Dexter': ['0'],'White Collar' : ['1','3']}
skipshow = {} 
#/Settings -----------------------------------------------------------------------------------------------------------------------------------------


# !!!! DO NOT MODIFY BEYOND THIS LINE !!!! ---------------------------------------------------------------------------------------------------------

api = "http://api.bierdopje.com/%s/" %apikey
rssUrl = "http://www.bierdopje.com/rss/subs/nl"
showid_cache = {}

# The following 3 lines convert the skipshow to uppercase. 
skipshowupper = {}
for x in skipshow: 
	skipshowupper[x.upper()] = skipshow[x]

LOGLEVEL=logging.DEBUG
LOGSIZE= 100000000
LOGNUM = 10
logfile= "AutoSubService.log"

# initialize logging
# A log directory has to be created below the start directory
log = logging.getLogger("thelogger")
log.setLevel(LOGLEVEL)

log_script = logging.handlers.RotatingFileHandler(logfile, 'a', LOGSIZE, LOGNUM)
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


help_message = '''
Usage:
	-h (--help)	Prints this message
	

Example:
	python AutoSub.py
'''

def SkipShow(showName,season,episode):
	if showName.upper() in skipshowupper.keys():
		log.debug("SkipShow: Found %s in skipshow dictonary" %showName)
		for seasontmp in skipshowupper[showName.upper()]:
			if seasontmp == '0':
				log.debug("SkipShow: variable of %s is set to 0, skipping the complete Serie" %showName)
				return True
			elif seasontmp == season:
				log.debug("SkipShow: Season matches variable of %s, skipping season" %showName)
				return True											
		
def ProcessFileName(file):
	processedFilenameResults = {}
	title = None
	season = None 
	episode = None 
	episodeid = None 
	quality = None 
	releasegrp = None 
	source = None 
	episodeidstart = None

	file = file.lower()
	
	# Try to determine the TV Episode information
	if re.search('[sS][0-9][0-9][eE][0-9][0-9]', file): 
		#s01e05
		result = re.search('[sS][0-9][0-9][eE][0-9][0-9]', file)
		episodeid = str(result.group(0))
		
		#episodeidstart = result.start(0) - 1
		episodeidstart = result.start(0)
		int(episodeidstart)
		
		season = episodeid[2]
		if episodeid[4] == "0":
			episode = episodeid[5]
		if not episodeid[4] == "0":
			episode = episodeid[4] + episodeid[5]
		
	elif re.search('[0-9][0-9][0-9]', file):
		#105
		result = re.search('[0-9][0-9][0-9]', file)
		episodeid = str(result.group(0))
	
		#episodeidstart = result.start(0) - 1
		episodeidstart = result.start(0)
		int(episodeidstart)
		
		season = episodeid[0]
		if episodeid[1] == "0":
			episode = episodeid[2]
		if not episodeid[1] == "0":
			episode = episodeid[1] + episodeid[2]
			
	elif re.search('[sS][0-9][0-9][xX][eE][0-9][0-9]', file):
		result = re.search('[sS][0-9][0-9][xX][eE][0-9][0-9]', file)

		#S00xE00
		episodeid = str(result.group(0))
		
		episodeidstart = result.start(0) - 1
		int(episodeidstart)
	
		season = episodeid[2]
		if episodeid[4] == "0":
			episode = episodeid[5]
		if not episodeid[4] == "0":
			episode = episodeid[4] + episodeid[5]
				
	elif re.search('[0-9][xX][0-9][0-9]', file):
		#1x05
		result = re.search('[0-9][xX][0-9][0-9]', file)
		episodeid = str(result.group(0))
		
		episodeidstart = result.start(0) - 1
		int(episodeidstart)
	
		season = episodeid[0]
		if episodeid[2] == "0":
			episode = episodeid[3]
		if not episodeid[2] == "0":
			episode = episodeid[2] + episodeid[2]
	
	
	#Determine Quality
	if re.search('720', file):
		quality = '720'
	elif re.search('1080', file):
		quality = '1080'
	else:
		tempSplitname = file.split(".")
		ext = tempSplitname[len(tempSplitname)-1]
		
		if ext  == 'mkv': 
			quality = '720'
		else:
			quality = 'SD'
	
	# Determine source
	if re.search('hdtv', file): 
		source = 'hdtv'
	if re.search('dvdrip', file): 
		source = 'dvdrip'
	if re.search('bdrip', file): 
		source = 'bdrip'
	if re.search('blueray', file): 
		source = 'bluray'
	if re.search('web-dl', file): 
		source = 'web-dl'
	
	# Convential naming:
	# True.Blood.S02E06.REPACK.720p.BluRay.X264-REWARD
	# The.Big.Bang.Theory.S04E23.HDTV.XviD-FQM.ext
	# The.Big.Bang.Theory.S04E22.REPACK.720p.HDTV.x264-CTU.ext
	# The.Big.Bang.Theory.S04E24.WEB-DL.720p.DD5.1.H.ext
	# Non convential naming:
	# TV Episode - S01E01.ext
	tempString = str.replace(file,"repack.","")
	tempString = str.replace(tempString,"proper.","")
	splittedTempString = tempString.split(".")
	
	if splittedTempString[len(splittedTempString)-1] in ('srt','mkv','avi','mpg','ts'):
		splittedTempString.pop(len(splittedTempString)-1)
	
	if len(splittedTempString) > 2:
		# it appears to have atleast 1 more . in it aside from the extension
		# grab the last bit
		toTestString = splittedTempString[len(splittedTempString)-1]
		
		# test if this is a release group:
		if toTestString[:5] == "x264-":	
			releasegrp = toTestString.split("-")[1]
		if toTestString[:4] == "264-":	
			releasegrp = toTestString.split("-")[1]
		if toTestString[:5] == "xvid-": 
			releasegrp = toTestString.split("-")[1]
		
	if episodeidstart:
		title = file[:episodeidstart]
		title = str.replace(title,"."," ")
		title = str.replace(title,"-"," ")
		title = str.replace(title," -","")
		title = str.replace(title,"- ","")
		title = title.rstrip()
		title = title.lstrip()
		title = str.title(title)
	
	if title: processedFilenameResults['title'] = title
	if season: processedFilenameResults['season'] = season
	if episode: processedFilenameResults['episode'] = episode
	if quality: processedFilenameResults['quality'] = quality
	if source: processedFilenameResults['source'] = source
	if releasegrp: processedFilenameResults['releasegrp'] = releasegrp
	
	log.debug("ProcessFileName: Returning %s" %processedFilenameResults)
	
	return processedFilenameResults

	
def getShowid(showName):
	getShowIdUrl = "%sGetShowByName/%s" %(api, urllib.quote(showName))
	
	req = urllib2.urlopen(getShowIdUrl)
	dom = minidom.parse(req)
	req.close()
		
	if not dom or len(dom.getElementsByTagName('showid')) == 0 :
		return None
	
	showid = dom.getElementsByTagName('showid')[0].firstChild.data
	return showid

def nameMapping(showName):
	if showName in namemapping.keys():
		log.debug("nameMapping: found match for %s" %showName)
		return namemapping[showName]

def matchQuality(quality, item):
	if quality == "SD":
		if re.search('720', item): 
			log.debug("matchQuality: Quality SD did not match to %s" %item)
			return None
		elif re.search('1080', item): 
			log.debug("matchQuality: Quality SD did not match to %s" %item)
			return None
		else:
			log.debug("matchQuality: Quality matched SD to %s" %item)
			return 1
	elif quality == "1080" and re.search('1080', item):
		log.debug("matchQuality: Quality is 1080 matched to %s" %item)
		return 1
	elif quality == "720" and re.search('720', item):
		log.debug("matchQuality: Quality is 720 matched to %s" %item)
		return 1

def getSubLink(showid, lang, releaseDetails):
	quality = None
	releasegrp = None
	source = None
	season = releaseDetails['season']
	episode = releaseDetails['episode']
	
	getSubLinkUrl = "%sGetAllSubsFor/%s/%s/%s/%s" %(api, showid, season, episode, lang)
	req = urllib2.urlopen(getSubLinkUrl)
	dom = minidom.parse(req)
	req.close()
	
	if 'quality' in releaseDetails.keys(): quality = releaseDetails['quality']
	if 'releasegrp' in releaseDetails.keys(): releasegrp = releaseDetails['releasegrp']
	if 'source' in releaseDetails.keys(): source = releaseDetails['source']
	
	if not dom or len(dom.getElementsByTagName('result')) == 0 :
		return None
	
	for sub in dom.getElementsByTagName('result'):
		release = sub.getElementsByTagName('filename')[0].firstChild.data
		release = release.lower()
		if release.endswith(".srt"):
			release = release[:-4]
		
		# Try to determine the attributes required to make a match on bierdopje
		# 0 Match on Quality (HD1080/HD720/SD), Release Group and Source --> 100% hit
		# 1 Match on Quality (HD1080/HD720/SD), Release Group --> 95% hit
		# 2 Match on Quality (HD1080/HD720/SD), Source --> 75% hit
		# 3 Match on Quality (HD1080/HD720/SD) --> 50% hit
		# 4 Blind match
		
		if quality and releasegrp and source:
			log.debug("getSubLink: Trying to match against Quality & Releasegrp & Source") 
			if matchQuality(quality, release) and re.search(releasegrp, release) and re.search(source, release):
				return sub.getElementsByTagName('downloadlink')[0].firstChild.data
			
		elif quality and releasegrp and not source:
			log.debug("getSubLink: Trying to match against Quality & Releasegrp")
			if matchQuality(quality, release) and re.search(releasegrp, release):
				return sub.getElementsByTagName('downloadlink')[0].firstChild.data
				
		elif quality and source and not releasegrp:
			log.debug("getSubLink: Trying to match against Quality & Source")
			if matchQuality(quality, release) and re.search(source, release):
				return sub.getElementsByTagName('downloadlink')[0].firstChild.data
				
		elif quality and not source and not releasegrp:
			log.debug("getSubLink: Trying to match against Quality")
			
			if matchQuality(quality, release):
				return sub.getElementsByTagName('downloadlink')[0].firstChild.data				

		elif not quality and not source and not releasegrp:
			log.debug("getSubLink: Making a blind match because ProcessFileName could not determine anything")
			return sub.getElementsByTagName('downloadlink')[0].firstChild.data

def checkRSS(wantedQueue, toDownloadQueue):	
	log.debug("checkRSS: Starting round of RSS checking")
	req = urllib2.urlopen(rssUrl)
	dom = minidom.parse(req)
	
	if not dom or len(dom.getElementsByTagName('result')) == 0:
		rssTitleList = dom.getElementsByTagName('title')
		normalizedRssTitleList = []
		
		for rssTitle in rssTitleList:
			log.debug("checkRSS: Normalizing the following entry in the RSS results: %s" %rssTitle.firstChild.data)
			normalizedRssTitle = ProcessFileName(str(rssTitle.firstChild.data))
			if 'title' in normalizedRssTitle.keys():
				if 'season' in normalizedRssTitle.keys():
					if 'episode' in normalizedRssTitle.keys():		
						normalizedRssTitleList.append(normalizedRssTitle)

		#check versus wantedItem list
		for index, wantedItem in enumerate(wantedQueue):
			wantedItemquality = None
			wantedItemreleasegrp = None
			wantedItemsource = None
			wantedItemtitle = wantedItem['title']
			wantedItemseason = wantedItem['season']
			wantedItemepisode = wantedItem['episode']
					
			if 'quality' in wantedItem.keys(): wantedItemquality = wantedItem['quality']
			if 'releasegrp' in wantedItem.keys(): wantedItemreleasegrp = wantedItem['releasegrp']
			if 'source' in wantedItem.keys(): wantedItemsource = wantedItem['source']
			
			if wantedItemtitle in showid_cache.keys():
				showid = showid_cache[wantedItemtitle]
			
			if not wantedItemtitle in showid_cache.keys():
				showid = getShowid(wantedItemtitle)
				if not showid: 
					log.debug("checkRSS: Could not be found on bierdopje.com for %s, trying the namemapping" %wantedItemtitle)
					showid = nameMapping(wantedItemtitle)
					if not showid:
						log.error("checkRSS: Could not find a show ID for %s" %wantedItemtitle)
						continue
				showid_cache[wantedItemtitle] = showid
			
			for normalizedRssTitle in normalizedRssTitleList:
				toDownloadItem = None
				downloadLink = None
				normalizedRssTitlequality = None
				normalizedRssTitlereleasegrp = None
				normalizedRssTitlesource = None
				normalizedRssTitletitle = normalizedRssTitle['title']
				normalizedRssTitleseason = normalizedRssTitle['season']
				normalizedRssTitleepisode = normalizedRssTitle['episode']
						
				if 'quality' in normalizedRssTitle.keys(): normalizedRssTitlequality = normalizedRssTitle['quality']
				if 'releasegrp' in normalizedRssTitle.keys(): normalizedRssTitlereleasegrp = normalizedRssTitle['releasegrp']
				if 'source' in normalizedRssTitle.keys(): normalizedRssTitlesource = normalizedRssTitle['source']
				
				if wantedItemtitle == normalizedRssTitletitle and wantedItemseason == normalizedRssTitleseason and wantedItemepisode == normalizedRssTitleepisode:
					log.debug("checkRSS:  The episode %s - Season %s Episode %s was found in the RSS list, attempting to match a proper match" %(wantedItemtitle, wantedItemseason,wantedItemepisode))
					
					if wantedItemquality and wantedItemreleasegrp and wantedItemsource:
						log.debug("checkRSS: Trying to match against Quality & Releasegrp & Source") 
						if wantedItemquality == normalizedRssTitlequality and wantedItemreleasegrp == normalizedRssTitlereleasegrp and wantedItemsource == normalizedRssTitlesource:
							log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" %(wantedItemtitle, wantedItemseason,wantedItemepisode))
							downloadLink = getSubLink(showid, "nl", wantedItem)
						
					elif wantedItemquality and wantedItemreleasegrp and not wantedItemsource:
						log.debug("checkRSS: Trying to match against Quality & Releasegrp")
						if wantedItemquality == normalizedRssTitlequality and wantedItemreleasegrp == normalizedRssTitlereleasegrp:
							log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" %(wantedItemtitle, wantedItemseason,wantedItemepisode))
							downloadLink = getSubLink(showid, "nl", wantedItem)
							
					elif wantedItemquality and wantedItemsource and not wantedItemreleasegrp:
						log.debug("checkRSS: Trying to match against Quality & Source")
						if wantedItemquality == normalizedRssTitlequality and wantedItemsource == normalizedRssTitlesource:
							log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" %(wantedItemtitle, wantedItemseason,wantedItemepisode))
							downloadLink = getSubLink(showid, "nl", wantedItem)
							
					elif wantedItemquality and not wantedItemsource and not wantedItemreleasegrp:
						log.debug("checkRSS: Trying to match against Quality")
						
						if wantedItemquality == normalizedRssTitlequality:
							log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" %(wantedItemtitle, wantedItemseason,wantedItemepisode))
							downloadLink = getSubLink(showid, "nl", wantedItem)				

					if downloadLink: 
						originalfile = wantedItem['originalFileLocationOnDisk']
						srtfile = os.path.join(originalfile[:-4] + ".srt")
						
						wantedItem['downloadLink'] = downloadLink
						wantedItem['destinationFileLocationOnDisk'] = srtfile
						toDownloadQueue.append(wantedItem)
						log.info("checkRSS: The episode %s - Season %s Episode %s has a matching subtitle on bierdopje, adding to toDownloadQueue" %(wantedItemtitle, wantedItemseason,wantedItemepisode))
						wantedQueue.pop(index)
						log.debug("checkRSS: Removed item: %s from the wantedQueue at index %s" %(wantedItem, index))
		
	log.debug("checkRSS: Finished round of RSS checking")
	return wantedQueue, toDownloadQueue

def downloadSubs(toDownloadQueue):
	for index, downloadItem in enumerate(toDownloadQueue):
		if 'destinationFileLocationOnDisk' in downloadItem.keys() and 'downloadLink' in downloadItem.keys():
			destsrt = downloadItem['destinationFileLocationOnDisk']
			downloadLink = downloadItem['downloadLink']
	
			try:
				response = urllib2.urlopen(downloadLink)
			except:
				log.error("downloadSubs: Error while opening the downloadLink: %s" %downloadLink)
				continue				
			
			try:
				open(destsrt,'w').write(response.read())
			except:
				log.error("downloadSubs: Error while writing subtitle file. Destination: %s" %destsrt)
				continue
			
			log.info("downloadSubs: DOWNLOADED: %s" %destsrt)
			toDownloadQueue.pop(index)
			log.debug("downloadSubs: Removed item: %s from the toDownloadQueue at index %s" %(downloadItem, index))
		else:
			log.error("downloadSub: No downloadLink or locationOnDisk found at downloadItem, skipping")
			continue
	
	return toDownloadQueue
	
def scanDir(rootpath):
	wantedQueue = []
	log.debug("scanDir: Starting round of local disk checking")
	
	for dirname, dirnames, filenames in os.walk(os.path.join(rootpath)):
		for filename in filenames:			
			splitname = filename.split(".")
			ext = splitname[len(splitname)-1]
			
			if ext in ('avi','mkv','wmv','ts'):
				if re.search('sample', filename): continue
				
				srtfile = os.path.join(filename[:-4] + ".srt")
				
				if not os.path.exists(os.path.join(dirname,srtfile)):
					log.debug("scanDir: File %s does not yet have a srt file" %filename)				
					filenameResults = ProcessFileName(filename)
					
					if 'title' in filenameResults.keys():
						
						if 'season' in filenameResults.keys():
							if 'episode' in filenameResults.keys():
								title = filenameResults['title']
								season = filenameResults['season']
								episode = filenameResults['episode']
								
								if SkipShow(title, season, episode)==True:
									log.debug("scanDir: SkipShow returned True")
									log.info("scanDir: Skipping %s - Season %s Episode %s" %(title, season,episode))
									continue
								
								filenameResults['originalFileLocationOnDisk'] = os.path.join(dirname,filename)
								wantedQueue.append(filenameResults)
								log.info("scanDir: File %s added to wantedQueue" %filename)								
							else:
								log.error("scanDir: Could not process the filename properly filename: %s" %filename)
								continue


	log.debug("scanDir: Finished round of local disk checking")
	return wantedQueue

def checkSub(wantedQueue, toDownloadQueue):
	log.debug("checkSub: Starting round of checkSub")
	for index, wantedItem in enumerate(wantedQueue):
		title = wantedItem['title']
		season = wantedItem['season']
		episode = wantedItem['episode']
		originalfile = wantedItem['originalFileLocationOnDisk']
		
		srtfile = os.path.join(originalfile[:-4] + ".srt")
		engsrtfile = os.path.join(originalfile[:-4] + ".eng.srt") 
		
		if title in showid_cache.keys():
			showid = showid_cache[title]
		
		if not title in showid_cache.keys():
			showid = getShowid(title)
			if not showid: 
				log.debug("checkSub: Could not be found on bierdopje.com for %s, trying the namemapping" %title)
				showid = nameMapping(title)
				if not showid:
					log.error("checkSub: Could not find a show ID for %s" %title)
					continue
			log.debug("checkSub: Got the following showid: %s" %showid)
			showid_cache[title] = showid
		
		downloadLink = getSubLink(showid, "nl", wantedItem)

		if not downloadLink:
			if fallbackToEng == False:
				log.debug("checkSub: No dutch subtitles found on bierdopje.com for %s - Season %s - Episode %s" %(title, season,episode))
				continue
			if os.path.exists(engsrtfile) and fallbackToEng == True:
				log.info("checkSub: The english subtitle is found, will try again later for the dutch version %s - Season %s - Episode %s" %(title, season,episode))
				continue
			if not os.path.exists(engsrtfile) and fallbackToEng == True:
				log.debug("checkSub: Dutch subtitle could not be found on bierdopje.com, checking for the english version for %s - Season %s - Episode %s" %(title, season,episode))
				downloadLink = getSubLink(showid, "en", wantedItem)
				if not downloadLink:
					log.info("checkSub: No english subtitles found on bierdopje.com for %s - Season %s - Episode %s" %(title, season,episode))
					continue
				elif downloadLink:
					wantedItem['downloadLink'] = downloadLink
					wantedItem['destinationFileLocationOnDisk'] = engsrtfile
					toDownloadQueue.append(wantedItem)
					continue
		elif downloadLink:
			wantedItem['downloadLink'] = downloadLink
			wantedItem['destinationFileLocationOnDisk'] = srtfile
			toDownloadQueue.append(wantedItem)
			log.info("checkSub: The episode %s - Season %s Episode %s has a matching subtitle on bierdopje, adding to toDownloadQueue" %(title,season,episode))
			wantedQueue.pop(index)
			log.debug("checkSub: Removed item: %s from the wantedQueue at index %s" %(wantedItem, index))
	
	log.debug("checkSub: Finished round of checkSub")	
	return wantedQueue, toDownloadQueue
	
class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg
	
def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts = getopt.getopt(argv[1:], "h", ["help"])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		for option in opts:
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
	
	#initial scan&check
	wantedQueue = scanDir(rootpath)
	wantedQueue, toDownloadQueue = checkSub(wantedQueue, toDownloadQueue)
	
	# take timestamps
	ts_scanDir = time.time()
	ts_checkSub = time.time()
	ts_checkRSS = time.time()
	
	while True:
		#every tick check for length if not 0: do Download
		if len(toDownloadQueue) > 0:
			log.info("main: Found %s items in toDownloadQueue, running downloadSubs" %(len(toDownloadQueue)))
			toDownloadQueue = downloadSubs(toDownloadQueue)
		
		#once every hour
		if time.time() - ts_scanDir > 3600:
			log.info("main: Haven't run scanDir for %s minutes, running scanDir" %(round((time.time() - ts_scanDir)/60)))
			wantedQueue = scanDir(rootpath)
			ts_scanDir = time.time()
			continue
		
		#once every 8 hours
		if time.time() - ts_checkSub > 28800:
			log.info("main: Haven't run checkSub for %s minutes, running checkSub" %(round((time.time() - ts_checkSub)/60)))
			wantedQueue, toDownloadQueue = checkSub(wantedQueue, toDownloadQueue)
			ts_checkSub = time.time()
			continue
		
		#once every 5 minutes
		if time.time() - ts_checkRSS > 300: 
			log.info("main: Haven't run checkRSS for %s minutes, running checkRSS" %(round((time.time() - ts_checkRSS)/60)))
			wantedQueue, toDownloadQueue = checkRSS(wantedQueue, toDownloadQueue)
			ts_checkRSS = time.time()
			continue
	
		log.info("main: wantedQueue #: %s - toDownloadQueue #: %s" %(len(wantedQueue),len(toDownloadQueue)))
		#tick = set smallest timediff required
		time.sleep(300)

if __name__ == "__main__":
	sys.exit(main())
