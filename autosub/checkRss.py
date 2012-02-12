# Autosub Db.py - http://code.google.com/p/auto-sub/
#
# The Autosub checkRss module
#

import logging
import urllib2
import os

from xml.dom import minidom
#from operator import itemgetter

import autosub.Helpers
import autosub.Bierdopje

log = logging.getLogger('thelogger')

# TODO: checkRss need to support the new matching system
class checkRss():
    """
    Check the RSS feed for subtitles of episodes that are in the WANTEDQUEUE.
    If the subtitles are found, they are added to the TODOWNLOADQUEUE
    """
    def run(self):    
        log.debug("checkRSS: Starting round of RSS checking")

        if autosub.TODOWNLOADQUEUELOCK or autosub.WANTEDQUEUELOCK:
            log.debug("checkRSS: Exiting, another threat is using the queues")
            return False
        else:
            autosub.TODOWNLOADQUEUELOCK = True
            autosub.WANTEDQUEUELOCK = True

        toDelete_wantedQueue = []

        langs = ["nl"]
        # default is to only check for Dutch subs
        # but if English should be downloaden, check them to
        if autosub.FALLBACKTOENG or autosub.DOWNLOADENG:
            langs.append("en")
            log.debug("checkRSS: We also want to check the English RSS feed")
        
        for lang in langs:
            if lang == "en":
                RSSURL = autosub.ENRSSURL
                log.debug("checkRSS: Now using the English RSS feed")
            else:
                RSSURL = autosub.NLRSSURL
                log.debug("checkRSS: Now using the Dutch RSS feed")

            try:  
                req = urllib2.urlopen(RSSURL)
                dom = minidom.parse(req)
                req.close()
            except:
                # Because of the latest problems with the RSS feed, the progress will return as if all went ok.
                log.error("checkRss: The server returned an error for request %s" % RSSURL)
                autosub.TODOWNLOADQUEUELOCK = False
                autosub.WANTEDQUEUELOCK = False
                log.info("checkRss: Retrying later, something is wrong with the network connect or with the bierdopje rssfeed.")
                return True
    
            if not dom or len(dom.getElementsByTagName('result')) == 0:
                rssTitleList = dom.getElementsByTagName('title')
                normalizedRssTitleList = []
    
                for rssTitle in rssTitleList:
                    log.debug("checkRSS: Normalizing the following entry in the RSS results: %s" % rssTitle.firstChild.data)
                    normalizedRssTitle = autosub.Helpers.ProcessFileName(str(rssTitle.firstChild.data), '')
                    if 'title' in normalizedRssTitle.keys():
                        if 'season' in normalizedRssTitle.keys():
                            if 'episode' in normalizedRssTitle.keys():        
                                normalizedRssTitleList.append(normalizedRssTitle)
    
                #check versus wantedItem list
                for index, wantedItem in enumerate(autosub.WANTEDQUEUE):
                    wantedItemquality = None
                    wantedItemreleasegrp = None
                    wantedItemsource = None
                    wantedItemtitle = wantedItem['title']
                    wantedItemseason = wantedItem['season']
                    wantedItemepisode = wantedItem['episode']
    
                    if 'quality' in wantedItem.keys(): wantedItemquality = wantedItem['quality']
                    if 'releasegrp' in wantedItem.keys(): wantedItemreleasegrp = wantedItem['releasegrp']
                    if 'source' in wantedItem.keys(): wantedItemsource = wantedItem['source']
    
                    if wantedItemtitle in autosub.SHOWID_CACHE.keys():
                        showid = autosub.SHOWID_CACHE[wantedItemtitle]
    
                    if not wantedItemtitle in autosub.SHOWID_CACHE.keys():
                        showid = autosub.Bierdopje.getShowid(wantedItemtitle)
                        if not showid:
                            log.debug("checkRSS: Could not be found on bierdopje.com for %s, trying the namemapping" % wantedItemtitle)
                            showid = autosub.Helpers.nameMapping(wantedItemtitle)
                            if not showid:
                                log.error("checkRSS: Could not find a show ID for %s" % wantedItemtitle)
                                continue
                        autosub.SHOWID_CACHE[wantedItemtitle] = showid
    
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
                            log.debug("checkRSS:  The episode %s - Season %s Episode %s was found in the RSS list, attempting to match a proper match" % (wantedItemtitle, wantedItemseason, wantedItemepisode))
    
                            if wantedItemquality and wantedItemreleasegrp and wantedItemsource:
                                log.debug("checkRSS: Trying to match against Quality & Releasegrp & Sourcefor %s - Season %s Episode %s" %(wantedItemtitle, wantedItemseason, wantedItemepisode))
                                if wantedItemquality == normalizedRssTitlequality and wantedItemreleasegrp == normalizedRssTitlereleasegrp and wantedItemsource == normalizedRssTitlesource:
                                    log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" % (wantedItemtitle, wantedItemseason, wantedItemepisode))
                                    downloadLink = autosub.Bierdopje.getSubLink(showid, "nl", wantedItem)
    
                            elif wantedItemquality and wantedItemreleasegrp and not wantedItemsource:
                                log.debug("checkRSS: Trying to match against Quality & Releasegrpfor %s - Season %s Episode %s" % (wantedItemtitle, wantedItemseason, wantedItemepisode))
                                if wantedItemquality == normalizedRssTitlequality and wantedItemreleasegrp == normalizedRssTitlereleasegrp:
                                    log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink"  % (wantedItemtitle, wantedItemseason, wantedItemepisode))
                                    downloadLink = autosub.Bierdopje.getSubLink(showid, lang, wantedItem)
    
                            elif wantedItemquality and wantedItemsource and not wantedItemreleasegrp:
                                log.debug("checkRSS: Trying to match against Quality & Source")
                                if wantedItemquality == normalizedRssTitlequality and wantedItemsource == normalizedRssTitlesource:
                                    log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" % (wantedItemtitle, wantedItemseason, wantedItemepisode))
                                    downloadLink = autosub.Bierdopje.getSubLink(showid, lang, wantedItem)
    
                            elif wantedItemquality and not wantedItemsource and not wantedItemreleasegrp:
                                log.debug("checkRSS: Trying to match against Quality for %s - Season %s Episode %s" % (wantedItemtitle, wantedItemseason, wantedItemepisode))
    
                                if wantedItemquality == normalizedRssTitlequality:
                                    log.debug("Found a match for %s - Season %s Episode %s, getting downloadLink" % (wantedItemtitle, wantedItemseason, wantedItemepisode))
                                    downloadLink = autosub.Bierdopje.getSubLink(showid, lang, wantedItem)                
    
                            if downloadLink:
                                originalfile = wantedItem['originalFileLocationOnDisk']
                                # Dutch subs
                                if autosub.SUBNL != "" and lang == "nl":
                                    srtfile = os.path.join(originalfile[:-4] + "." + autosub.SUBNL + ".srt")
                                elif lang == "nl":
                                    srtfile = os.path.join(originalfile[:-4] + ".srt")
                                # English subs
                                if autosub.SUBENG != "" and lang == "en":
                                    srtfile = os.path.join(originalfile[:-4] + "." + autosub.SUBENG + ".srt")
                                elif lang == "en":
                                    srtfile = os.path.join(originalfile[:-4] + ".srt")
                                wantedItem['downloadLink'] = downloadLink
                                wantedItem['destinationFileLocationOnDisk'] = srtfile
                                autosub.TODOWNLOADQUEUE.append(wantedItem)
                                log.info("checkRSS: The episode %s - Season %s Episode %s has a matching subtitle on bierdopje, adding to toDownloadQueue" % (wantedItemtitle, wantedItemseason, wantedItemepisode))
                                toDelete_wantedQueue.append(index)
                                break
    
            i = len(toDelete_wantedQueue)-1
            while i >= 0:
                log.debug("checkRSS: Removed item from the wantedQueue at index %s" % toDelete_wantedQueue[i])
                autosub.WANTEDQUEUE.pop(toDelete_wantedQueue[i])
                i = i-1
    
        log.debug("checkRSS: Finished round of RSS checking")
        autosub.TODOWNLOADQUEUELOCK = False
        autosub.WANTEDQUEUELOCK = False
        return True
