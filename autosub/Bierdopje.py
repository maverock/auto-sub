# Autosub Bierdopje.py - http://code.google.com/p/auto-sub/
#
# The Bierdopje API module
#

import urllib
import urllib2
import logging

from xml.dom import minidom
from operator import itemgetter

import autosub.Helpers

# Settings
log = logging.getLogger('thelogger')


def getShowid(showName):
    """
    Search for the showid by using the Bierdopje API and the name of the show.
    Using showid for future searches reduces the load on the Bierdopje servers.

    Keyword arguments:
    showName -- Name of the show to search the showid for
    """
    api = autosub.API

    getShowIdUrl = "%sGetShowByName/%s" % (api, urllib.quote(showName))
    try:
        req = urllib2.urlopen(getShowIdUrl)
        dom = minidom.parse(req)
        req.close()
    except:
        log.error("getShowid: The server returned an error for request %s" % getShowIdUrl)
        return None

    if not dom or len(dom.getElementsByTagName('showid')) == 0:
        return None

    showid = dom.getElementsByTagName('showid')[0].firstChild.data
    return showid


def getSubLink(showid, lang, releaseDetails):
    """
    Return the link to download the best matching subtitle.
    Matching is based on the provided release details.

    Keyword arguments:
    showid -- The id of the show on Bierdopje
    lang -- Language of the wanted subtitle, Dutch or English
    releaseDetails -- Dict containing the quality, releasegrp, source season and episode.
    """
    api = autosub.API

    if showid == -1:
        return None
    quality = None
    releasegrp = None
    source = None
    season = releaseDetails['season']
    episode = releaseDetails['episode']

    getSubLinkUrl = "%sGetAllSubsFor/%s/%s/%s/%s" % (api, showid, season, episode, lang)

    try:
        req = urllib2.urlopen(getSubLinkUrl)
        dom = minidom.parse(req)
        req.close()
    except:
        log.error("getSubLink: The server returned an error for request %s" % getSubLinkUrl)
        return None

    if 'quality' in releaseDetails.keys(): quality = releaseDetails['quality']
    if 'releasegrp' in releaseDetails.keys(): releasegrp = releaseDetails['releasegrp']
    if 'source' in releaseDetails.keys(): source = releaseDetails['source']

    if not dom or len(dom.getElementsByTagName('result')) == 0:
        return None

    scoredict = {}

    for sub in dom.getElementsByTagName('result'):
        release = sub.getElementsByTagName('filename')[0].firstChild.data
        release = release.lower()
        # Remove the .srt extension some of the uploaders leave on the file
        if release.endswith(".srt"):
            release = release[:-4]
        # Scoredict is a dictionary with a download link and its match score. This will be used to determine the best match (the highest matchscore)
        scoredict[sub.getElementsByTagName('downloadlink')[0].firstChild.data] = autosub.Helpers.scoreMatch(release, quality, releasegrp, source)
        if scoredict[sub.getElementsByTagName('downloadlink')[0].firstChild.data] == 7:
            # Sometimes you just find a perfect match, why should we continue to search if we got a perfect match?
            log.debug('getSubLink: A perfect match found, returning the download link')
            return sub.getElementsByTagName('downloadlink')[0].firstChild.data
    # Done comparing all the results, lets sort them and return the highest result
    # If there are results with the same score, the download links which comes first (alphabetically) will be returned
    return sorted(scoredict.items(), key=itemgetter(1), reverse=True)[0][0]
