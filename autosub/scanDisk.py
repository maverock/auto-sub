# Autosub Db.py - http://code.google.com/p/auto-sub/
#
# The Autosub scanDisk module
#

import logging
import os
import re

# Autosub specific modules
import autosub
import autosub.Helpers
# Settings
log = logging.getLogger('thelogger')


class scanDisk():
    """
    Scan the specified path for episodes without Dutch or (if wanted) English subtitles.
    If found add these Dutch or English subtitles to the WANTEDQUEUE.
    """
    def run(self):
        log.debug("scanDir: Starting round of local disk checking at %s" % autosub.ROOTPATH)
        if autosub.WANTEDQUEUELOCK == True:
            log.debug("scanDir: Exiting, another threat is using the queues")
            return False
        else:
            autosub.WANTEDQUEUELOCK = True
        autosub.WANTEDQUEUE = []

        if not os.path.exists(autosub.ROOTPATH):
            log.error("Root path does %s not exists, aborting..." % autosub.ROOTPATH)
            exit()

        for dirname, dirnames, filenames in os.walk(os.path.join(autosub.ROOTPATH)):
            if re.search('_unpack_', dirname, re.IGNORECASE): 
                log.debug("scanDisk: found a unpack directory, skipping")
                continue
            
            if re.search('_failed_', dirname, re.IGNORECASE): 
                log.debug("scanDisk: found a failed directory, skipping")
                continue
            
            for filename in filenames:
                splitname = filename.split(".")
                ext = splitname[len(splitname) - 1]

                if ext in ('avi', 'mkv', 'wmv', 'ts', 'mp4'):
                    if re.search('sample', filename): continue

                    # What subtitle files should we expect?
                    if (autosub.SUBNL != ""):
                        srtfile = os.path.join(filename[:-4] + "." + autosub.SUBNL + ".srt")
                    else:
                        srtfile = os.path.join(filename[:-4] + ".srt")

                    srtfileeng = os.path.join(filename[:-4] + "." + autosub.SUBENG + ".srt")

                    if not os.path.exists(os.path.join(dirname, srtfile)) or (not os.path.exists(os.path.join(dirname, srtfileeng)) and autosub.DOWNLOADENG):
                        log.debug("scanDir: File %s is missing a subtitle" % filename)
                        lang = []
                        filenameResults = autosub.Helpers.ProcessFileName(os.path.splitext(filename)[0], os.path.splitext(filename)[1])
                        if 'title' in filenameResults.keys():
                            if 'season' in filenameResults.keys():
                                if 'episode' in filenameResults.keys():
                                    title = filenameResults['title']
                                    season = filenameResults['season']
                                    episode = filenameResults['episode']

                                    if autosub.Helpers.SkipShow(title, season, episode) == True:
                                        log.debug("scanDir: SkipShow returned True")
                                        log.info("scanDir: Skipping %s - Season %s Episode %s" % (title, season, episode))
                                        continue
                                    log.info("scanDir: Dutch subtitle wanted for %s and added to wantedQueue" % filename)
                                    filenameResults['originalFileLocationOnDisk'] = os.path.join(dirname, filename)
                                    
                                    if not os.path.exists(os.path.join(dirname, srtfile)):
                                        lang.append('nl')
                                    if not os.path.exists(os.path.join(dirname, srtfileeng)) and (autosub.FALLBACKTOENG or autosub.DOWNLOADENG):
                                        lang.append('en')
                                    
                                    filenameResults['lang'] = lang
                                    autosub.WANTEDQUEUE.append(filenameResults)
                                    
                                else:
                                    log.error("scanDir: Could not process the filename properly filename: %s" % filename)
                                    continue
                            else:
                                log.error("scanDir: Could not process the filename properly filename: %s" % filename)
                                continue
                        else:
                            log.error("scanDir: Could not process the filename properly filename: %s" % filename)
                            continue
                    
        log.debug("scanDir: Finished round of local disk checking")
        autosub.WANTEDQUEUELOCK = False
        autosub.WIPSTATUS.runnow = True
        return True
