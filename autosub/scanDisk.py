import logging
import os
import re
 
# Autosub specific modules
import autosub
import autosub.Helpers
# Settings
log = logging.getLogger('thelogger')
 
class scanDisk():
    def run(self):
        log.debug("scanDir: Starting round of local disk checking at %s" %autosub.ROOTPATH)
        if autosub.WANTEDQUEUELOCK==True:
            log.debug("scanDir: Exiting, another threat is using the queues")
            return False
        else:
            autosub.WANTEDQUEUELOCK=True
        autosub.WANTEDQUEUE = []
        
        
        if not os.path.exists(autosub.ROOTPATH):
            log.error("Root path does %s not exists, aborting..." %autosub.ROOTPATH)
            exit()
        
        for dirname, dirnames, filenames in os.walk(os.path.join(autosub.ROOTPATH)):
            for filename in filenames:            
                splitname = filename.split(".")
                ext = splitname[len(splitname)-1]
                
                if ext in ('avi','mkv','wmv','ts','mp4'):
                    if re.search('sample', filename): continue
                    
                    # What subtitle files should we expect?
                    if (autosub.SUBNL!=""):
                        srtfile = os.path.join(filename[:-4] + "." + autosub.SUBNL +".srt")
                    else:
                        srtfile = os.path.join(filename[:-4] + ".srt")
                    
                    srtfileeng = os.path.join(filename[:-4] + "." + autosub.SUBENG +".srt")
                    
                    if not os.path.exists(os.path.join(dirname,srtfile)):
                        log.debug("scanDir: File %s does not yet have a srt file" %filename)
                        # Helpers.ProcessFileName requires 2 arguments, the filename and the extension                
                        filenameResults = autosub.Helpers.ProcessFileName(os.path.splitext(filename)[0],os.path.splitext(filename)[1])
                        
                        if 'title' in filenameResults.keys():
                            
                            if 'season' in filenameResults.keys():
                                if 'episode' in filenameResults.keys():
                                    title = filenameResults['title']
                                    season = filenameResults['season']
                                    episode = filenameResults['episode']
                                    
                                    if autosub.Helpers.SkipShow(title, season, episode)==True:
                                        log.debug("scanDir: SkipShow returned True")
                                        log.info("scanDir: Skipping %s - Season %s Episode %s" %(title, season,episode))
                                        continue
                                    
                                    filenameResults['originalFileLocationOnDisk'] = os.path.join(dirname,filename)
                                    filenameResults['lang'] = 'nl'
                                    log.info("scanDir: Dutch subtitle wanted for %s and added to wantedQueue" %filename) 
                                    
                                    autosub.WANTEDQUEUE.append(filenameResults)
                                else:
                                    log.error("scanDir: Could not process the filename properly filename: %s" %filename)
                                    continue
                            else:
                                log.error("scanDir: Could not process the filename properly filename: %s" %filename)
                                continue
                        else:
                            log.error("scanDir: Could not process the filename properly filename: %s" %filename)
                            continue
                        
                    if not os.path.exists(os.path.join(dirname,srtfileeng)) and autosub.DOWNLOADENG == True:
                        log.debug("scanDir: File %s does not yet have a English srt file" %filename)
                        # Helpers.ProcessFileName requires 2 arguments, the filename and the extension                
                        filenameResults = autosub.Helpers.ProcessFileName(os.path.splitext(filename)[0],os.path.splitext(filename)[1])
                        
                        if 'title' in filenameResults.keys():
                            if 'season' in filenameResults.keys():
                                if 'episode' in filenameResults.keys():
                                    title = filenameResults['title']
                                    season = filenameResults['season']
                                    episode = filenameResults['episode']
                                    
                                    if autosub.Helpers.SkipShow(title, season, episode)==True:
                                        log.debug("scanDir: SkipShow returned True")
                                        log.info("scanDir: Skipping %s - Season %s Episode %s" %(title, season,episode))
                                        continue
                                    
                                    filenameResults['originalFileLocationOnDisk'] = os.path.join(dirname,filename)
                                    filenameResults['lang'] = 'en'
                                    log.info("scanDir: English subtitle wanted for %s and added to wantedQueue" %filename) 
                                    
                                    autosub.WANTEDQUEUE.append(filenameResults)
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
        autosub.WANTEDQUEUELOCK=False
        autosub.WIPSTATUS.runnow = True
        return True