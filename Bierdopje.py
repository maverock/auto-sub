# Autosub Bierdopje.py - http://code.google.com/p/auto-sub/
#
# The Bierdopje API module
# 

import Helpers

import urllib
import urllib2
import os
import re
import logging

from xml.dom import minidom
from operator import itemgetter
# Settings
log = logging.getLogger('thelogger')
apikey = "AFC34E2C2FE8B9F7"

api = "http://api.bierdopje.com/%s/" %apikey
rssUrl = "http://www.bierdopje.com/rss/subs/nl"
# /Settings

# Autosub modules
import Config

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

def getSubLink(showid, lang, releaseDetails):
	if showid==-1:
	    return None
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
	
	scoredict = {}

	for sub in dom.getElementsByTagName('result'):
		release = sub.getElementsByTagName('filename')[0].firstChild.data
		release = release.lower()
		# Remove the .srt extension some of the uploaders leave on the file
		if release.endswith(".srt"):
			release = release[:-4]
		# Scoredict is a dictionary with a download link and its match score. This will be used to determine the best match (the highest matchscore)
		scoredict[sub.getElementsByTagName('downloadlink')[0].firstChild.data] = Helpers.scoreMatch(release, quality, releasegrp, source)
		if scoredict[sub.getElementsByTagName('downloadlink')[0].firstChild.data] == 7:
			# Sometimes you just find a perfect match, why should we continue to search if we got a perfect match?
			log.debug('getSubLink: A perfect match found, returning the download link')
			return sub.getElementsByTagName('downloadlink')[0].firstChild.data
	# Done comparing all the results, lets sort them and return the highest result
	# If there are results with the same score, the download links which comes first (alphabetically) will be returned
	return sorted(scoredict.items(), key=itemgetter(1), reverse=True)[0][0]


def checkRSS(wantedQueue, toDownloadQueue):	
	log.debug("checkRSS: Starting round of RSS checking")
	toDelete_wantedQueue = []
	
	try:  
		req = urllib2.urlopen(rssUrl)
		dom = minidom.parse(req)
		req.close()
	except:  
		log.error("getSubLink: The server returned an error for request %s" %rssUrl)
		return wantedQueue, toDownloadQueue
	
	if not dom or len(dom.getElementsByTagName('result')) == 0:
		rssTitleList = dom.getElementsByTagName('title')
		normalizedRssTitleList = []
		
		for rssTitle in rssTitleList:
			log.debug("checkRSS: Normalizing the following entry in the RSS results: %s" %rssTitle.firstChild.data)
			normalizedRssTitle = Helpers.ProcessFileName(str(rssTitle.firstChild.data),'')
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
			
			if wantedItemtitle in Config.Properties.showid_cache.keys():
				showid = Config.Properties.showid_cache[wantedItemtitle]
			
			if not wantedItemtitle in Config.Properties.showid_cache.keys():
				showid = getShowid(wantedItemtitle)
				if not showid: 
					log.debug("checkRSS: Could not be found on bierdopje.com for %s, trying the namemapping" %wantedItemtitle)
					showid = Config.nameMapping(wantedItemtitle)
					if not showid:
						log.error("checkRSS: Could not find a show ID for %s" %wantedItemtitle)
						continue
				Config.Properties.showid_cache[wantedItemtitle] = showid
			
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
						break
	
	i=len(toDelete_wantedQueue)-1
	while i >= 0: 
		log.debug("checkRSS: Removed item from the wantedQueue at index %s" %toDelete_wantedQueue[i])
		wantedQueue.pop(toDelete_wantedQueue[i])
		i=i-1
	
	log.debug("checkRSS: Finished round of RSS checking")
	return wantedQueue, toDownloadQueue

def checkSub(wantedQueue, toDownloadQueue):
	log.debug("checkSub: Starting round of checkSub")
	toDelete_wantedQueue = []
	
	for index, wantedItem in enumerate(wantedQueue):
		title = wantedItem['title']
		season = wantedItem['season']
		episode = wantedItem['episode']
		originalfile = wantedItem['originalFileLocationOnDisk']
		
		if Config.Properties.subnl!="":
			srtfile = os.path.join(originalfile[:-4] + "." + Config.Properties.subnl + ".srt")
		else:
			srtfile = os.path.join(originalfile[:-4] + ".srt")
		
		engsrtfile = os.path.join(originalfile[:-4] + "."+ Config.Properties.subeng +".srt")
		
		if title in Config.Properties.showid_cache.keys():
			showid = Config.Properties.showid_cache[title]
		
		if not title in Config.Properties.showid_cache.keys():
			showid = Config.nameMapping(title)
			if not showid: 
				log.debug("checkSub: no NameMapping found for %s, trying the Bierdopje API" %title)
				showid = getShowid(title)
				if not showid:
					log.error("checkSub: Could not find a show ID for %s" %title)
					Config.Properties.showid_cache[title] = -1
					continue
			log.debug("checkSub: Got the following showid: %s" %showid)
			Config.Properties.showid_cache[title] = showid
		
		log.debug("checkSub: trying to get a downloadlink for %s" % originalfile)
		
		downloadLink = getSubLink(showid, "nl", wantedItem)
		
		if not downloadLink:
			if Config.Properties.fallbackToEng == False:
				log.debug("checkSub: No dutch subtitles found on bierdopje.com for %s - Season %s - Episode %s" %(title, season,episode))
				continue
			if os.path.exists(engsrtfile) and Config.Properties.fallbackToEng == True:
				log.info("checkSub: The english subtitle is found, will try again later for the dutch version %s - Season %s - Episode %s" %(title, season,episode))
				continue
			if not os.path.exists(engsrtfile) and Config.Properties.fallbackToEng == True:
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