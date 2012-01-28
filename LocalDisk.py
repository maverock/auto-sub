# Autosub LocalDisk.py - http://code.google.com/p/auto-sub/
#
# The Autosub local disk io module
# 

import urllib
import urllib2
import os
import re
import logging

# Autosub specific modules
import Helpers
import Config

# Settings
log = logging.getLogger('thelogger')

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
			
			if Config.Properties.postprocesscmd:
				postprocesscmdconstructed = Config.Properties.postprocesscmd + " '" + downloadItem["destinationFileLocationOnDisk"] + "' '" + downloadItem["originalFileLocationOnDisk"] + "'"
				log.debug("downloadSubs: Postprocess: running %s" %postprocesscmdconstructed)
				log.info("downloadSubs: Running PostProcess")
				postprocessoutput,postprocesserr = Helpers.RunCmd(postprocesscmdconstructed)
				if postprocesserr:
					log.error("downloadSubs: PostProcess: %s" %postprocesserr)
				log.debug("downloadSubs: PostProcess Output:% s" %postprocessoutput)
			
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
					# Helpers.ProcessFileName requires 2 arguments, the filename and the extension				
					filenameResults = Helpers.ProcessFileName(os.path.splitext(filename)[0],os.path.splitext(filename)[1])
					
					if 'title' in filenameResults.keys():
						
						if 'season' in filenameResults.keys():
							if 'episode' in filenameResults.keys():
								title = filenameResults['title']
								season = filenameResults['season']
								episode = filenameResults['episode']
								
								if Config.SkipShow(title, season, episode)==True:
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
