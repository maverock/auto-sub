# Autosub Db.py - http://code.google.com/p/auto-sub/
#
# The Autosub downloadSubs module
#

import logging
import urllib2

import autosub

log = logging.getLogger('thelogger')


class downloadSubs():
    """
    Check the TODOWNLOADQUEUE and try to download everything in it.
    """
    def run(self):
        if len(autosub.TODOWNLOADQUEUE) > 0:
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
                        response = urllib2.urlopen(downloadLink)
                    except:
                        log.error("downloadSubs: The server returned an error for request %s" % downloadLink)
                        continue

                    try:
                        open(destsrt, 'w').write(response.read())
                    except:
                        log.error("downloadSubs: Error while writing subtitle file. Destination: %s" % destsrt)
                        continue

                    log.info("downloadSubs: DOWNLOADED: %s" % destsrt)
                    toDelete_toDownloadQueue.append(index)

                    if len(autosub.LASTESTDOWNLOAD) >= 10:
                        autosub.LASTESTDOWNLOAD.pop(0)
                        autosub.LASTESTDOWNLOAD.append(autosub.TODOWNLOADQUEUE[index])
                    else:
                        autosub.LASTESTDOWNLOAD.append(autosub.TODOWNLOADQUEUE[index])

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
