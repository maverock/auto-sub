# Autosub Helpers.py - http://code.google.com/p/auto-sub/
#
# The Autosub helper functions
# 

import urllib
import urllib2
import logging
import re
import os
from string import capwords

# Settings
log = logging.getLogger('thelogger')

REGEXES = [
		re.compile("^((?P<title>.+?)[. _-]+)?s(?P<season>\d+)[x. _-]*e(?P<episode>\d+)(([. _-]*e|-)(?P<extra_ep_num>(?!(1080|720)[pi])\d+))*[. _-]*((?P<quality>(1080|720|SD))*[pi]*[. _-]*(?P<source>(hdtv|dvdrip|bdrip|blu[e]*ray|web[. _-]*dl))*[. _]*(?P<extra_info>.+?)((?<![. _-])-(?P<releasegrp>[^-]+))?)?$",re.IGNORECASE),
		re.compile("^((?P<title>.+?)[\[. _-]+)?(?P<season>\d+)x(?P<episode>\d+)(([. _-]*x|-)(?P<extra_ep_num>(?!(1080|720)[pi])\d+))*[. _-]*((?P<quality>(1080|720|SD))*[pi]*[. _-]*(?P<source>(hdtv|dvdrip|bdrip|blu[e]*ray|web[. _-]*dl))*[. _]*(?P<extra_info>.+?)((?<![. _-])-(?P<releasegrp>[^-]+))?)?$",re.IGNORECASE),
		re.compile("^(?P<title>.+?)[. _-]+(?P<season>\d{1,2})(?P<episode>\d{2})([. _-]*(?P<quality>(1080|720|SD))*[pi]*[. _-]*(?P<source>(hdtv|dvdrip|bdrip|blu[e]*ray|web[. _-]*dl))*[. _]*(?P<extra_info>.+?)((?<![. _-])-(?P<releasegrp>[^-]+))?)?$",re.IGNORECASE)
		]
QUALITY_PARSER = re.compile("(hdtv|tv|dvdrip|dvd|bdrip|blu[e]*ray|web[. _-]*dl)",re.IGNORECASE)

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

def ReturnUpper(text):
	#This is a simple function which just tries to convert text to upper case when not possible it does nothing
	try:
		text = text.upper()
		return text
	except:
		pass

def ProcessFileName(file):
	processedFilenameResults = {}
	title = None			#The Show Name
	season = None 			#Season number
	episode = None 			#Episode number
	quality = None 			#quality, can either be 1080, 720 or SD
	releasegrp = None 		#The Release group
	source = None 			#The source, can either be hdtv, dvdrip, bdrip, blueray or web-dl
	matchdic = {}
	
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
	if 'title' in matchdic.keys(): title = CleanSerieName(matchdic["title"])
	if 'season' in matchdic.keys(): season = matchdic["season"]
	if 'episode' in matchdic.keys(): episode = matchdic["episode"]
	if 'source' in matchdic.keys(): 
		source =  ReturnUpper(matchdic["source"])
		if source != None:
			source = re.sub("[. _-]", "-", source)  
	if 'releasegrp' in matchdic.keys(): releasegrp = matchdic["releasegrp"]
	if 'quality' in matchdic.keys(): quality = ReturnUpper(matchdic["quality"])

	# Fallback for the quality and source mkv files and mp4 are most likely HD quality
	# Other files are more likely sd quality
	# Will search the file for a couple of possible sources, also parse out dots and dashes and replace with a dash
	if source == None:
		results = re.search(QUALITY_PARSER,filesplit)
		try:
			source = results.group(0)
			source = re.sub("[. _-]", "-", source) 
			#The following four rules are there to support the file naming SickBeard used (like: Serie.Name.S01E02.SD.TV.avi
			if source == 'tv':
				source = 'hdtv'
			if source == 'dvd':
				source = 'dvdrip'
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
		