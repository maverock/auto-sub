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
namemapping = {}
#/Settings -----------------------------------------------------------------------------------------------------------------------------------------


# !!!! DO NOT MODIFY BEYOND THIS LINE !!!! ---------------------------------------------------------------------------------------------------------

api = "http://api.bierdopje.com/%s/" %apikey
showid_cache = {}


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
	
	log.debug("ProcessFileName: Resolved %s to the following episodeid %s" %(file, episodeid))
	log.debug("ProcessFileName: Resolved season %s and episode %s" %(season, episode))
	
	#Determine Quality
	if re.search('720', file):
		log.debug("ProcessFileName: Quality is 720")
		quality = '720'
	elif re.search('1080', file):
		log.debug("ProcessFileName: Quality is 1080")
		quality = '1080'
	else:
		log.debug("ProcessFileName: Could not determine quality, making a best effort on the extension")
		tempSplitname = file.split(".")
		ext = splitname[len(splitname)-1]
		
		if ext in ('avi', 'ts', 'wmv'): 
			log.debug("ProcessFileName: Setted the quality to HDTV based on %s" %ext)
			quality = 'SD'
		if ext in ('mkv'): 
			log.debug("ProcessFileName: Setted the quality to 720 based on %s" %ext)
			quality = '720'
	
	# Determine source
	if re.search('hdtv', file): 
		log.debug("ProcessFileName: Source is HDTV")
		source = 'hdtv'
	if re.search('dvdrip', file): 
		log.debug("ProcessFileName: Source is DVDrip")
		source = 'dvdrip'
	if re.search('bdrip', file): 
		log.debug("ProcessFileName: Source is BDrip")
		source = 'bdrip'
	if re.search('blueray', file): 
		log.debug("ProcessFileName: Source is BluRay")
		source = 'bluray'
	if re.search('web-dl', file): 
		log.debug("ProcessFileName: Source is WEB-DL")
		source = 'web-dl'
	
	#Determine release group
	
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
	
	if len(splittedTempString) > 2:
		# it appears to have atleast 1 more . in it aside from the extension
		# grab the last bit before the file extension
		toTestString = splittedTempString[len(splittedTempString)-2]
		
		# test if this is a release group:
		if toTestString[:5] == "x264-":	
			releasegrp = toTestString.split("-")[1]
			log.debug("ProcessFileName: Resolved the following release group: %s" %releasegrp)
		if toTestString[:4] == "264-":	
			releasegrp = toTestString.split("-")[1]
			log.debug("ProcessFileName: Resolved the following release group: %s" %releasegrp)
		if toTestString[:5] == "xvid-": 
			releasegrp = toTestString.split("-")[1]
			log.debug("ProcessFileName: Resolved the following release group: %s" %releasegrp)
		
	if episodeidstart:
		title = file[:episodeidstart]
		title = str.replace(title,"."," ")
		title = str.replace(title,"-"," ")
		title = str.replace(title," -","")
		title = str.replace(title,"- ","")
		title = title.rstrip()
		title = title.lstrip()
		title = str.title(title)
		log.debug("ProcessFileName: Resolved the following title: %s" %title)
	
	if title: processedFilenameResults['title'] = title
	if season: processedFilenameResults['season'] = season
	if episode: processedFilenameResults['episode'] = episode
	if quality: processedFilenameResults['quality'] = quality
	if source: processedFilenameResults['source'] = source
	if releasegrp: processedFilenameResults['releasegrp'] = releasegrp
	
	log.debug("ProcessFileName: Returning %s" %processedFilenameResults)
	
	return processedFilenameResults

	
def getShowid(showName):
	if showName in namemapping.keys():
		return namemapping['showid']

	getShowIdUrl = "%sGetShowByName/%s" %(api, urllib.quote(showName))
	
	req = urllib2.urlopen(getShowIdUrl)
	dom = minidom.parse(req)
	req.close()
		
	if not dom or len(dom.getElementsByTagName('showid')) == 0 :
		return None
	
	showid = dom.getElementsByTagName('showid')[0].firstChild.data
	return showid

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
		
while True:
	log.debug("Starting round of local disk checking")
	
	for dirname, dirnames, filenames in os.walk(os.path.join(rootpath)):
		for filename in filenames:			
			splitname = filename.split(".")
			ext = splitname[len(splitname)-1]
			
			if ext in ('avi','mkv','wmv','ts'):
				if re.search('sample', filename): continue
				
				srtfile = os.path.join(filename[:-4] + ".srt")
				engsrtfile = os.path.join(filename[:-4] + ".eng.srt") 
				
				if not os.path.exists(os.path.join(dirname,srtfile)):
					log.debug("Filename %s does not yet have a srt file" %filename)
					filenameResults = ProcessFileName(filename)
					
					if 'title' in filenameResults.keys():
						if 'season' in filenameResults.keys():
							if 'episode' in filenameResults.keys():
								title = filenameResults['title']
								season = filenameResults['season']
								episode = filenameResults['episode']
							else:
								log.error("Could not process the filename properly filename: %s" %filename)
								continue

					if title in showid_cache.keys():
						showid = showid_cache[title]
						log.debug("Got the following showid from cache: %s" %showid)
					
					if not title in showid_cache.keys():
						showid = getShowid(title)
						log.debug("Got the following showid from bierdopje.com: %s" %showid)
						if not showid: 
							log.error("Could not be found on bierdopje.com, skipping %s" %title)
							continue
							
						showid_cache[title] = showid
					
					downloadLink = getSubLink(showid, "nl", filenameResults)
					destsrt = os.path.join(dirname,srtfile)
					
					if not downloadLink:
						if fallbackToEng == False:
							log.debug("No subtitles found on bierdopje.com for %s" %filename)
							continue
						if os.path.exists(os.path.join(dirname,engsrtfile)) and fallbackToEng == True:
							log.debug("The ENG subtitle is found, will try again later for the dutch version %s" %filename)
							continue
						if not os.path.exists(os.path.join(dirname,engsrtfile)) and fallbackToEng == True:
							log.debug("Dutch subtitle could not be found on bierdopje.com, attempting to download the english version for %s" %filename)
							downloadLink = getSubLink(showid, "en", filenameResults)
							destsrt = os.path.join(dirname,engsrtfile)
							
							if not downloadLink:
								log.debug("No subtitles found on bierdopje.com for %s" %filename)
								continue
							
					if downloadLink:
						response = urllib2.urlopen(downloadLink)
						log.info("DOWNLOADING the following link: %s" %downloadLink)
											
						try:
							open(destsrt,'w').write(response.read())
						except:
							log.error("Error while writing subtitle file. Destination: %s" %destsrt)
							exit()
						
						log.info("DOWNLOADED: %s" %destsrt)

	log.debug("Finished round of local disk checking")
	time.sleep(3600)
