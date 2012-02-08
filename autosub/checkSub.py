import logging
import os

# Autosub specific modules
import autosub.Bierdopje

# Settings
log = logging.getLogger('thelogger')

class checkSub():
    def run(self):
        log.debug("checkSub: Starting round of checkSub")
        toDelete_wantedQueue = []
        
        if autosub.TODOWNLOADQUEUELOCK or autosub.WANTEDQUEUELOCK:
            log.debug("checkSub: Exiting, another threat is using the queues")
            return False
        else:
            autosub.TODOWNLOADQUEUELOCK=True
            autosub.WANTEDQUEUELOCK=True
        
        for index, wantedItem in enumerate(autosub.WANTEDQUEUE):
            title = wantedItem['title']
            season = wantedItem['season']
            episode = wantedItem['episode']
            originalfile = wantedItem['originalFileLocationOnDisk']
            language = wantedItem['lang']
            
            if autosub.SUBNL!="":
                srtfile = os.path.join(originalfile[:-4] + "." + autosub.SUBNL + ".srt")
            else:
                srtfile = os.path.join(originalfile[:-4] + ".srt")
            
            engsrtfile = os.path.join(originalfile[:-4] + "."+ autosub.SUBENG +".srt")
            
            if title in autosub.SHOWID_CACHE.keys():
                showid = autosub.SHOWID_CACHE[title]
            
            if not title in autosub.SHOWID_CACHE.keys():
                showid = autosub.Helpers.nameMapping(title)
                if not showid: 
                    log.debug("checkSub: no NameMapping found for %s, trying the Bierdopje API" %title)
                    showid = autosub.Bierdopje.getShowid(title)
                    if not showid:
                        log.error("checkSub: Could not find a show ID for %s" %title)
                        autosub.SHOWID_CACHE[title] = -1
                        continue
                log.debug("checkSub: Got the following showid: %s" %showid)
                autosub.SHOWID_CACHE[title] = showid
            
            log.debug("checkSub: trying to get a downloadlink for %s, language is %s" % (originalfile,language))
            
            downloadLink = autosub.Bierdopje.getSubLink(showid, language, wantedItem)
            
            if not downloadLink and language == 'nl' and not autosub.DOWNLOADENG:
                if autosub.FALLBACKTOENG == False:
                    log.debug("checkSub: No dutch subtitles found on bierdopje.com for %s - Season %s - Episode %s" %(title, season,episode))
                    continue
                if os.path.exists(engsrtfile) and autosub.FALLBACKTOENG == True:
                    log.info("checkSub: The english subtitle is found, will try again later for the dutch version %s - Season %s - Episode %s" %(title, season,episode))
                    continue
                if not os.path.exists(engsrtfile) and autosub.FALLBACKTOENG == True:
                    log.debug("checkSub: Dutch subtitle could not be found on bierdopje.com, checking for the english version for %s - Season %s - Episode %s" %(title, season,episode))
                    downloadLink = autosub.Bierdopje.getSubLink(showid, "en", wantedItem)
                    if not downloadLink:
                        log.info("checkSub: No english subtitles found on bierdopje.com for %s - Season %s - Episode %s" %(title, season,episode))
                        continue
                    elif downloadLink:
                        wantedItem['downloadLink'] = downloadLink
                        wantedItem['destinationFileLocationOnDisk'] = engsrtfile
                        autosub.TODOWNLOADQUEUE.append(wantedItem)
                        continue
            elif not downloadLink and language == 'en':
                log.info('checkSub: no english subtitle found on bierdopje.com for %s - Season %s - Episode %s' %(title, season,episode))
                continue
            
            elif downloadLink:
                wantedItem['downloadLink'] = downloadLink
                if language == 'nl':
                    wantedItem['destinationFileLocationOnDisk'] = srtfile
                elif language == 'en':
                    wantedItem['destinationFileLocationOnDisk'] = engsrtfile
                autosub.TODOWNLOADQUEUE.append(wantedItem)
                log.info("checkSub: The episode %s - Season %s Episode %s has a matching subtitle on bierdopje, adding to toDownloadQueue" %(title,season,episode))
                log.debug("checkSub: destination filename %s" %wantedItem['destinationFileLocationOnDisk'])
                toDelete_wantedQueue.append(index)
                log.debug("checkSub: Removed item: %s from the wantedQueue at index %s" %(wantedItem, index))
        
        
        i=len(toDelete_wantedQueue)-1
        while i >= 0: 
            log.debug("checkSub: Removed item from the wantedQueue at index %s" %toDelete_wantedQueue[i])
            autosub.WANTEDQUEUE.pop(toDelete_wantedQueue[i])
            i=i-1
        
        log.debug("checkSub: Finished round of checkSub")    
        autosub.TODOWNLOADQUEUELOCK=False
        autosub.WANTEDQUEUELOCK=False
        return True