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
from string import capwords

from ConfigParser import SafeConfigParser

# Settings -----------------------------------------------------------------------------------------------------------------------------------------
# Location of the configuration file:
configfile = "config.properties"
# API key
apikey = "AFC34E2C2FE8B9F7"
# This dictionary maps local series names to BierDopje ID's
# Example: namemapping = {"Castle":"12708"}
namemapping = {
        "Greys Anatomy" : "3733",
        "Grey's Anatomy" : "3733",
        "Csi Miami" : "2187",
        "Mr Sunshine":"14224",
        "Spartacus Gods Of The Arena":"14848",
        "Spartacus Blood And Sand":"13942",
        "Hawaii Five 0":"14211"
}
#/Settings -----------------------------------------------------------------------------------------------------------------------------------------


# !!!! DO NOT MODIFY BEYOND THIS LINE !!!! ---------------------------------------------------------------------------------------------------------

api = "http://api.bierdopje.com/%s/" %apikey
rssUrl = "http://www.bierdopje.com/rss/subs/nl"
showid_cache = {}

# This dictionary can be use to skip shows or seasons from being downloaded. The seasons should be defined as lists
# Should be added in the property file as:
# [skipshow]
# Dexter=0
# White Collar=1,3
skipshow = {} 

# Read config file
try:
	cfg = SafeConfigParser()
	cfg.read(configfile)

	rootpath=cfg.get("config", "ROOTPATH")
	fallbackToEng=cfg.getboolean("config", "FALLBACKTOENG")
	subeng=cfg.get("config", "SUBENG")
	logfile= cfg.get("config", "LOGFILE")
except:
	rootpath = os.getcwd()
	fallbackToEng = True
	subeng="en"
	logfile="AutoSubService.log"
	
	cfg.add_section('config')
	cfg.set("config","ROOTPATH",rootpath)
	cfg.set("config","FALLBACKTOENG",str(fallbackToEng))
	cfg.set("config","SUBENG",subeng)
	cfg.set("config","LOGFILE",logfile)
	
	with open(configfile, 'wb') as file:
		cfg.write(file)

# Try to read skipshow section in the config
skipshow = dict(cfg.items('skipshow'))

# The following 4 lines convert the skipshow to uppercase. And also convert the variables to a list 
skipshowupper = {}
for x in skipshow:
	skipshowupper[x.upper()] = skipshow[x].split(',')

LOGLEVEL=logging.DEBUG
LOGSIZE= 100000000
LOGNUM = 10

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
REGEXES = [
		re.compile("^((?P<title>.+?)[. _-]+)?s(?P<season>\d+)[x. _-]*e(?P<episode>\d+)(([. _-]*e|-)(?P<extra_ep_num>(?!(1080|720)[pi])\d+))*[. _-]*((?P<quality>(1080|720))*[pi]*[. _-]*(?P<source>(hdtv|dvdrip|bdrip|blueray|web[. _-]*dl))*[. _]*(?P<extra_info>.+?)((?<![. _-])-(?P<releasegrp>[^-]+))?)?$",re.IGNORECASE),
		re.compile("^((?P<title>.+?)[\[. _-]+)?(?P<season>\d+)x(?P<episode>\d+)(([. _-]*x|-)(?P<extra_ep_num>(?!(1080|720)[pi])\d+))*[. _-]*((?P<quality>(1080|720))*[pi]*[. _-]*(?P<source>(hdtv|dvdrip|bdrip|blueray|web[. _-]*dl))*[. _]*(?P<extra_info>.+?)((?<![. _-])-(?P<releasegrp>[^-]+))?)?$",re.IGNORECASE),
		re.compile("^(?P<title>.+?)[. _-]+(?P<season>\d{1,2})(?P<episode>\d{2})([. _-]*(?P<quality>(1080|720))*[pi]*[. _-]*(?P<source>(hdtv|dvdrip|bdrip|blueray|web[. _-]*dl))*[. _]*(?P<extra_info>.+?)((?<![. _-])-(?P<releasegrp>[^-]+))?)?$",re.IGNORECASE)
		]
QUALITY_PARSER = re.compile("(hdtv|dvdrip|bdrip|blueray|web[. _-]*dl)",re.IGNORECASE)
def CleanSerieName(series_name):
	"""Cleans up series name by removing any . and _
    characters, along with any trailing hyphens.

    Is basically equivalent to replacing all _ and . with a
    space, but handles decimal numbers in string, for example:

    >>> cleanRegexedSeriesName("an.example.1.0.test")
    'an example 1.0 test'
    >>> cleanRegexedSeriesName("an_example_1.0_test")
    'an example 1.0 test'
    
    Stolen from dbr's tvnamer
    """

	series_name = re.sub("(\D)\.(?!\s)(\D)", "\\1 \\2", series_name)
	series_name = re.sub("(\d)\.(\d{4})", "\\1 \\2", series_name) # if it ends in a year then don't keep the dot
	series_name = re.sub("(\D)\.(?!\s)", "\\1 ", series_name)
	series_name = re.sub("\.(?!\s)(\D)", " \\1", series_name)
	series_name = series_name.replace("_", " ")
	series_name = re.sub("-$", "", series_name)
	return capwords(series_name.strip())

def SkipShow(showName,season,episode):
	if showName.upper() in skipshowupper.keys():
		log.debug("SkipShow: Found %s in skipshow dictonary" %showName)
		for seasontmp in skipshowupper[showName.upper()]:
			if seasontmp == '0':
				log.debug("SkipShow: variable of %s is set to 0, skipping the complete Serie" %showName)
				return True
			elif int(seasontmp) == int(season):
				log.debug("SkipShow: Season matches variable of %s, skipping season" %showName)
				return True											
	
def ProcessFileName(file):
	processedFilenameResults = {}
	title = None			#The Show Name
	season = None 			#Season number
	episode = None 			#Episode number
	quality = None 			#quality, can either be 1080, 720 or SD
	releasegrp = None 		#The Release group
	source = None 			#The source, can either be hdtv, dvdrip, bdrip, blueray or web-dl

	file = file.lower()
	filesplit = os.path.splitext(file)[0] #remove the file extension
	# Try to determine the TV Episode information
	for regexes in REGEXES: #Lets try all the regexpresions in REGEXES
		matches = regexes.search(filesplit)
		try:
			matchdic = matches.groupdict()
			log.debug("ProcessFileName: Hit with a regex, dumping it for debug purpose: " + str(matchdic))
			break #If we got a match, lets break
		except AttributeError:
			continue
	#Trying to set all the main attributes
					
	try:
		title = CleanSerieName(matchdic["title"])
		season = matchdic["season"]
		episode = matchdic["episode"]
		source =  matchdic["source"]
		source = re.sub("[. _-]", "-", source)  
		releasegrp = matchdic["releasegrp"]
		quality = matchdic["quality"]
	except:
		pass

	# Fallback for the quality and source mkv files and mp4 are most likely HD quality
	# Other files are more likely sd quality
	# Will search the file for a couple of possible sources, also parse out dots and dashes and replace with a dash
	if source == None:
		results = re.search(QUALITY_PARSER,filesplit)
		try:
			source = results.group(0)
			source = re.sub("[. _-]", "-", source) 
			log.debug("ProcessFileName: Fallback hit for source, source is %s" % source)
		except:
			pass

	if quality == None:
		filesplit2 = os.path.splitext(file)[1]
		if filesplit2 == ".mkv" or filesplit2 == ".mp4":
			quality = '720'
			log.debug("ProcessFileName: Fallback, file seems to be mkv or mp4 so best guess for quality would be 720")
		else:
			quality = 'SD'
			log.debug("ProcessFileName: Fallback, can't determine the quality so guess SD")

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
	
	try:  
		req = urllib2.urlopen(getShowIdUrl)
		dom = minidom.parse(req)
		req.close()
	except:  
		log.error("getShowid: The server returned an error for request %s" %getShowIdUrl)
		return None
	
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
	
	try:  
		req = urllib2.urlopen(getSubLinkUrl)
		dom = minidom.parse(req)
		req.close()
	except:  
		log.error("getSubLink: The server returned an error for request %s" %getSubLinkUrl)
		return None
	
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
			log.debug("getSubLink: Trying to match against Quality & Releasegrp & Source for %s" %release) 
			if matchQuality(quality, release) and re.search(releasegrp, release) and re.search(source, release):
				return sub.getElementsByTagName('downloadlink')[0].firstChild.data
			
		elif quality and releasegrp and not source:
			log.debug("getSubLink: Trying to match against Quality & Releasegrp for %s" %release)
			if matchQuality(quality, release) and re.search(releasegrp, release):
				return sub.getElementsByTagName('downloadlink')[0].firstChild.data
				
		elif quality and source and not releasegrp:
			log.debug("getSubLink: Trying to match against Quality & Source for %s" %release) 
			if matchQuality(quality, release) and re.search(source, release):
				return sub.getElementsByTagName('downloadlink')[0].firstChild.data
				
		elif quality and not source and not releasegrp:
			log.debug("getSubLink: Trying to match against Quality for %s" %release) 
			
			if matchQuality(quality, release):
				return sub.getElementsByTagName('downloadlink')[0].firstChild.data				

		elif not quality and not source and not releasegrp:
			log.debug("getSubLink: Making a blind match because ProcessFileName could not determine anything")
			return sub.getElementsByTagName('downloadlink')[0].firstChild.data

def checkRSS(wantedQueue, toDownloadQueue):	
	log.debug("checkRSS: Starting round of RSS checking")
	toDelete_wantedQueue = []
	
	try:  
		req = urllib2.urlopen(rssUrl)
		dom = minidom.parse(req)
		req.close()
	except:  
		log.error("getSubLink: The server returned an error for request %s" %rssUrl)
		return None
	
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
						log.debug("checkRSS: Trying to match against Quality & Releasegrp & Sourcefor %s - Season %s Episode %s"%(wantedItemtitle, wantedItemseason,wantedItemepisode))
						if wantedItemquality == normalizedRssTitlequality and wantedItemreleasegrp == normalizedRssTitlereleasegrp and wantedItemsource == normalizedRssTitlesource:
							log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" %(wantedItemtitle, wantedItemseason,wantedItemepisode))
							downloadLink = getSubLink(showid, "nl", wantedItem)
						
					elif wantedItemquality and wantedItemreleasegrp and not wantedItemsource:
						log.debug("checkRSS: Trying to match against Quality & Releasegrpfor %s - Season %s Episode %s"%(wantedItemtitle, wantedItemseason,wantedItemepisode))
						if wantedItemquality == normalizedRssTitlequality and wantedItemreleasegrp == normalizedRssTitlereleasegrp:
							log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" %(wantedItemtitle, wantedItemseason,wantedItemepisode))
							downloadLink = getSubLink(showid, "nl", wantedItem)
							
					elif wantedItemquality and wantedItemsource and not wantedItemreleasegrp:
						log.debug("checkRSS: Trying to match against Quality & Source")
						if wantedItemquality == normalizedRssTitlequality and wantedItemsource == normalizedRssTitlesource:
							log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" %(wantedItemtitle, wantedItemseason,wantedItemepisode))
							downloadLink = getSubLink(showid, "nl", wantedItem)
							
					elif wantedItemquality and not wantedItemsource and not wantedItemreleasegrp:
						log.debug("checkRSS: Trying to match against Quality for %s - Season %s Episode %s"%(wantedItemtitle, wantedItemseason,wantedItemepisode))
						
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
						toDelete_wantedQueue.append(index)
	
	i=len(toDelete_wantedQueue)-1
	while i >= 0: 
		log.debug("checkRSS: Removed item from the wantedQueue at index %s" %toDelete_wantedQueue[i])
		wantedQueue.pop(toDelete_wantedQueue[i])
		i=i-1
	
	log.debug("checkRSS: Finished round of RSS checking")
	return wantedQueue, toDownloadQueue

def downloadSubs(toDownloadQueue):
	toDelete_toDownloadQueue = []
	
	for index, downloadItem in enumerate(toDownloadQueue):
		if 'destinationFileLocationOnDisk' in downloadItem.keys() and 'downloadLink' in downloadItem.keys():
			destsrt = downloadItem['destinationFileLocationOnDisk']
			downloadLink = downloadItem['downloadLink']
	
			try:
				response = urllib2.urlopen(downloadLink)				
			except:  
				log.error("downloadSubs: The server returned an error for request %s" %downloadLink)
				continue
			
			try:
				open(destsrt,'w').write(response.read())
			except:
				log.error("downloadSubs: Error while writing subtitle file. Destination: %s" %destsrt)
				continue
			
			log.info("downloadSubs: DOWNLOADED: %s" %destsrt)
			toDelete_toDownloadQueue.append(index)
			#toDownloadQueue.remove(downloadItem)
		else:
			log.error("downloadSub: No downloadLink or locationOnDisk found at downloadItem, skipping")
			continue
	
	i=len(toDelete_toDownloadQueue)-1
	while i >= 0: 
		log.debug("downloadSubs: Removed item from the toDownloadQueue at index %s" %toDelete_toDownloadQueue[i])
		toDownloadQueue.pop(toDelete_toDownloadQueue[i])
		i=i-1

	return toDownloadQueue
	
def scanDir(rootpath):
	wantedQueue = []
	log.debug("scanDir: Starting round of local disk checking at %s" %rootpath)
	
	if not os.path.exists(rootpath):
		log.error("Root path does %s not exists, aborting..." %rootpath)
		exit()
	
	for dirname, dirnames, filenames in os.walk(os.path.join(rootpath)):
		for filename in filenames:			
			splitname = filename.split(".")
			ext = splitname[len(splitname)-1]
			
			if ext in ('avi','mkv','wmv','ts','mp4'):
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
						else:
							log.error("scanDir: Could not process the filename properly filename: %s" %filename)
							continue
					else:
						log.error("scanDir: Could not process the filename properly filename: %s" %filename)
						continue

	log.debug("scanDir: Finished round of local disk checking")
	return wantedQueue

def checkSub(wantedQueue, toDownloadQueue):
	log.debug("checkSub: Starting round of checkSub")
	toDelete_wantedQueue = []
	
	for index, wantedItem in enumerate(wantedQueue):
		title = wantedItem['title']
		season = wantedItem['season']
		episode = wantedItem['episode']
		originalfile = wantedItem['originalFileLocationOnDisk']
		
		srtfile = os.path.join(originalfile[:-4] + ".srt")
		engsrtfile = os.path.join(originalfile[:-4] + "."+subeng +".srt")
		
		if title in showid_cache.keys():
			showid = showid_cache[title]
		
		if not title in showid_cache.keys():
			showid = getShowid(title)
			if not showid: 
				log.debug("checkSub: The showid not be found on bierdopje.com for %s, trying the namemapping" %title)
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
			toDelete_wantedQueue.append(index)
			log.debug("checkSub: Removed item: %s from the wantedQueue at index %s" %(wantedItem, index))
	
	
	i=len(toDelete_wantedQueue)-1
	while i >= 0: 
		log.debug("checkSub: Removed item from the wantedQueue at index %s" %toDelete_wantedQueue[i])
		wantedQueue.pop(toDelete_wantedQueue[i])
		i=i-1
	
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
		
		#once every 8 hours
		if time.time() - ts_checkSub > 28800:
			log.info("main: Haven't run checkSub for %s minutes, running checkSub" %(round((time.time() - ts_checkSub)/60)))
			wantedQueue, toDownloadQueue = checkSub(wantedQueue, toDownloadQueue)
			ts_checkSub = time.time()
		
		#once every 5 minutes
		if time.time() - ts_checkRSS > 300: 
			log.info("main: Haven't run checkRSS for %s minutes, running checkRSS" %(round((time.time() - ts_checkRSS)/60)))
			wantedQueue, toDownloadQueue = checkRSS(wantedQueue, toDownloadQueue)
			ts_checkRSS = time.time()
	
		log.info("main: wantedQueue #: %s - toDownloadQueue #: %s" %(len(wantedQueue),len(toDownloadQueue)))
		#tick = set smallest timediff required
		time.sleep(300)

if __name__ == "__main__":
	sys.exit(main())
