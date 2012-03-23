# Autosub Db.py - http://code.google.com/p/auto-sub/
#
# The Autosub downloadSubs module
#

import logging
import urllib2

import autosub
import os

from autosub.Db import lastDown

log = logging.getLogger('thelogger')

class downloadSubs():
    """
    Check the TODOWNLOADQUEUE and try to download everything in it.
    """
    def run(self):
        if len(autosub.TODOWNLOADQUEUE) > 0:
            if not autosub.Helpers.checkAPICalls():
                log.warning("downloadSubs: out of api calls")
                return True
            
            toDelete_toDownloadQueue = []
            log.debug("downloadSubs: Something in downloadqueue, Starting downloadSubs")
            if autosub.TODOWNLOADQUEUELOCK or autosub.WANTEDQUEUELOCK:
                log.debug("downloadSubs: Exiting, another threat is using the queues")
                return False
            else:
                autosub.TODOWNLOADQUEUELOCK = True
                autosub.WANTEDQUEUELOCK = True
            for index, downloadItem in enumerate(autosub.TODOWNLOADQUEUE):
                if 'destinationFileLocationOnDisk' in downloadItem.keys() and 'downloadLink' in downloadItem.keys():
                    destsrt = downloadItem['destinationFileLocationOnDisk']
                    downloadLink = downloadItem['downloadLink']

                    try:
                        req = urllib2.Request(downloadLink)
                        req.add_header("User-agent", autosub.USERAGENT) 
                        log.debug("downloadSubs: Trying to download the following subtitle %s" %downloadLink)
                        response = urllib2.urlopen(req,None,autosub.TIMEOUT)
                        autosub.Helpers.checkAPICalls(use=True)
                    except:
                        log.error("downloadSubs: The server returned an error for request %s" % downloadLink)
                        continue
                    
                    destdir = os.path.split(destsrt)[0]
                    if not os.path.exists(destdir):
                        toDelete_toDownloadQueue.append(index)
                        log.debug("checkSubs: no destination directory %s" %destdir)
                        continue
                    elif not os.path.lexists(destdir):
                        log.debug("checkSubs: no destination directory %s" %destdir)
                        toDelete_toDownloadQueue.append(index)
                        continue
                    
                    try:
                        open(destsrt, 'wb').write(response.read())
                        response.close()
                    except:
                        log.error("downloadSubs: Error while writing subtitle file. Check if the destination is writeable! Destination: %s" % destsrt)
                        toDelete_toDownloadQueue.append(index)
                        continue

                    log.info("downloadSubs: DOWNLOADED: %s" % destsrt)
                    toDelete_toDownloadQueue.append(index)
                    
                    lastDown().setlastDown(dict = autosub.TODOWNLOADQUEUE[index])

                    if autosub.POSTPROCESSCMD:
                        postprocesscmdconstructed = autosub.POSTPROCESSCMD + ' "' + downloadItem["destinationFileLocationOnDisk"] + '" "' + downloadItem["originalFileLocationOnDisk"] + '"'
                        log.debug("downloadSubs: Postprocess: running %s" % postprocesscmdconstructed)
                        log.info("downloadSubs: Running PostProcess")
                        postprocessoutput, postprocesserr = autosub.Helpers.RunCmd(postprocesscmdconstructed)
                        if postprocesserr:
                            log.error("downloadSubs: PostProcess: %s" % postprocesserr)
                        log.debug("downloadSubs: PostProcess Output:% s" % postprocessoutput)

                    #toDownloadQueue.remove(downloadItem)
                else:
                    log.error("downloadSub: No downloadLink or locationOnDisk found at downloadItem, skipping")
                    continue

            i = len(toDelete_toDownloadQueue) - 1
            while i >= 0:
                log.debug("downloadSubs: Removed item from the toDownloadQueue at index %s" % toDelete_toDownloadQueue[i])
                autosub.TODOWNLOADQUEUE.pop(toDelete_toDownloadQueue[i])
                i = i - 1
            autosub.TODOWNLOADQUEUELOCK = False
            autosub.WANTEDQUEUELOCK = False
        return True
