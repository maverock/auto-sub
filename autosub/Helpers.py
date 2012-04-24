# Autosub Helpers.py - http://code.google.com/p/auto-sub/
#
# The Autosub helper functions
#

import logging
import re
import subprocess
from string import capwords
import time
import urllib2
#from distutils import version
from library import version
from autosub.version import autosubversion

import autosub

from autosub.Db import idCache
# Settings
log = logging.getLogger('thelogger')

REGEXES = [
        re.compile("^((?P<title>.+?)[. _-]+)?s(?P<season>\d+)[x. _-]*e(?P<episode>\d+)(([. _-]*e|-)(?P<extra_ep_num>(?!(1080|720)[pi])\d+))*[. _-]*((?P<quality>(1080|720|SD))*[pi]*[. _-]*(?P<source>(hdtv|dvdrip|bdrip|blu[e]*ray|web[. _-]*dl))*[. _]*(?P<extra_info>.+?)((?<![. _-])-(?P<releasegrp>[^-]+))?)?$", re.IGNORECASE),
        re.compile("^((?P<title>.+?)[\[. _-]+)?(?P<season>\d+)x(?P<episode>\d+)(([. _-]*x|-)(?P<extra_ep_num>(?!(1080|720)[pi])\d+))*[. _-]*((?P<quality>(1080|720|SD))*[pi]*[. _-]*(?P<source>(hdtv|dvdrip|bdrip|blu[e]*ray|web[. _-]*dl))*[. _]*(?P<extra_info>.+?)((?<![. _-])-(?P<releasegrp>[^-]+))?)?$", re.IGNORECASE),
        re.compile("^(?P<title>.+?)[. _-]+(?P<season>\d{1,2})(?P<episode>\d{2})([. _-]*(?P<quality>(1080|720|SD))*[pi]*[. _-]*(?P<source>(hdtv|dvdrip|bdrip|blu[e]*ray|web[. _-]*dl))*[. _]*(?P<extra_info>.+?)((?<![. _-])-(?P<releasegrp>[^-]+))?)?$", re.IGNORECASE)
        ]
SOURCE_PARSER = re.compile("(hdtv|tv|dvdrip|dvd|bdrip|blu[e]*ray|web[. _-]*dl)", re.IGNORECASE)
QUALITY_PARSER = re.compile("(1080|720|HD|SD)" , re.IGNORECASE)

def RunCmd(cmd):
    process = subprocess.Popen(cmd,
                            shell = True,
                            stdin = subprocess.PIPE,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE)
    shell = process.stdout.read()
    shellerr = process.stderr.read()
    process.wait()
    return shell, shellerr

def CheckVersion():
    try:
        req = urllib2.Request(autosub.VERSIONURL)
        req.add_header("User-agent", autosub.USERAGENT) 
        resp = urllib2.urlopen(req,None,autosub.TIMEOUT)
        respone = resp.read()
        resp.close()
    except:
        log.error("checkVersion: The server returned an error for request %s" % autosub.VERSIONURL)
        return None
    try:
        match = re.search('(Alpha|Beta|Stable) (\d+)\.(\d+)\.(\d+)', respone)
        version_online = match.group(0)
    except:
        return None
    
    release = version_online.split(' ')[0]
    versionnumber = version.StrictVersion(version_online.split(' ')[1])
    
    running_release = autosubversion.split(' ')[0]
    running_versionnumber = version.StrictVersion(autosubversion.split(' ')[1])
    
    if release == running_release:
        if versionnumber > running_versionnumber:
            return True
        else:
            return False
    else:
        return None

def CleanSerieName(series_name):
    """Clean up series name by removing any . and _
    characters, along with any trailing hyphens.

    Is basically equivalent to replacing all _ and . with a
    space, but handles decimal numbers in string, for example:

    >>> cleanRegexedSeriesName("an.example.1.0.test")
    'an example 1.0 test'
    >>> cleanRegexedSeriesName("an_example_1.0_test")
    'an example 1.0 test'

    Stolen from dbr's tvnamer
    """
    try:
        series_name = re.sub("(\D)\.(?!\s)(\D)", "\\1 \\2", series_name)
        series_name = re.sub("(\d)\.(\d{4})", "\\1 \\2", series_name)  # if it ends in a year then don't keep the dot
        series_name = re.sub("(\D)\.(?!\s)", "\\1 ", series_name)
        series_name = re.sub("\.(?!\s)(\D)", " \\1", series_name)
        series_name = series_name.replace("_", " ")
        series_name = re.sub("-$", "", series_name)
        return capwords(series_name.strip())
    except TypeError:
        log.debug("CleanSerieName: There is no SerieName to clean")


def ReturnUpper(text):
    """
    Return the text converted to uppercase.
    When not possible return nothing.
    """
    try:
        text = text.upper()
        return text
    except:
        pass


def ProcessFileName(filename, extension):
    """
    Process the file names, gather all the show information
    Input should be a filename
    
    Output is a dictionary with the following keys: 
    title, season, episode, source, quality, releasegrp
    """
    processedFilenameResults = {}
    title = None       # The Show Name
    season = None      # Season number
    episode = None     # Episode number
    quality = None     # quality, can either be 1080, 720 or SD
    releasegrp = None  # The Release group
    source = None      # The source, can either be hdtv, dvdrip, bdrip, blueray or web-dl
    extra_info = None  # All the information that couldn't be parsed
    matchdic = {}

    filename = filename.lower()
    # Try to determine the TV Episode information
    for regexes in REGEXES:  # Lets try all the regexpresions in REGEXES
        matches = regexes.search(filename)
        try:
            matchdic = matches.groupdict()
            log.debug("ProcessFileName: Hit with a regex, dumping it for debug purpose: " + str(matchdic))
            break  # If we got a match, lets break
        except AttributeError:
            continue
    # Trying to set all the main attributes
    if 'title' in matchdic.keys(): title = CleanSerieName(matchdic["title"])
    if 'season' in matchdic.keys(): season = matchdic["season"]
    if 'episode' in matchdic.keys(): episode = matchdic["episode"]
    if 'source' in matchdic.keys():
        source = matchdic["source"]
        if source != None:
            source = re.sub("[. _-]", "-", source)
    if 'releasegrp' in matchdic.keys(): releasegrp = matchdic["releasegrp"]
    if 'quality' in matchdic.keys(): quality = ReturnUpper(matchdic["quality"])  # Quality should be upper case, in case the quality is SD
    if 'extra_info' in matchdic.keys(): extra_info = matchdic["extra_info"]
    
    # Fallback for the quality and source mkv files are most likely HD quality
    # Other files are more likely sd quality
    # Will search the file for a couple of possible sources, also parse out dots and dashes and replace with a dash
    if source == None:
        if extra_info:
            # If we have extra info, lets try to find the source
            results = re.search(SOURCE_PARSER, extra_info)
            try:
                source = results.group(0)
                source = re.sub("[. _-]", "-", source)
                # The following four rules are there to support the file naming SickBeard used (like: Serie.Name.S01E02.SD.TV.avi
                if source == u'tv':
                    source = u'hdtv'
                if source == u'dvd':
                    source = u'dvdrip'
                log.debug("ProcessFileName: Fallback hit for source, source is %s" % source)
            except:
                pass
        
    if source == None:
        results = re.search(SOURCE_PARSER, filename)
        try:
            source = results.group(0)
            source = re.sub("[. _-]", "-", source)
            # The following four rules are there to support the file naming SickBeard used (like: Serie.Name.S01E02.SD.TV.avi
            if source == u'tv':
                source = u'hdtv'
            if source == u'dvd':
                source = u'dvdrip'
            log.debug("ProcessFileName: Fallback hit for source, source is %s" % source)
        except:
            pass

    if quality == None:
        if extra_info:
            # If we have extra info, lets try to find the quality
            results = re.search(QUALITY_PARSER, extra_info)
            try:
                quality = results.group(0)
                # Sickbeard renames files to HD if they are 720... So if HD is found as q, q should be 720.
                if quality == u'hd' and source != u'hdtv':
                    quality = u'720'
                else:
                    quality = None
                if quality:
                    quality = quality.upper() #in case quality is SD
                    log.debug("ProcessFileName: Fallback hit for quality, quality is %s" % quality)
            except:
                pass
            
    if quality == None:
        log.debug("ProcessFileName: No extra information. Falling back...")
        results = re.search(QUALITY_PARSER, filename)
        try:
            quality = results.group(0)
            # Sickbeard renames files to HD if they are 720... So if HD is found as q, q should be 720.
            if quality == u'hd' and source != u'hdtv':
                    quality = u'720'
            else:
                quality = None
            if quality:
                quality = quality.upper() #in case quality is SD
                log.debug("ProcessFileName: Fallback hit for quality, quality is %s" % quality)
        except:
            pass
            
    if quality == None:
        log.debug("ProcessFileName: Still not? -_-' Ok ok, last fallback... Trying to guess it by looking at the file extension")
        if extension == ".mkv":
            quality = u'720'
            log.debug("ProcessFileName: File seems to be mkv so best guess for quality would be 720")
        else:
            quality = u'SD'
            log.debug("ProcessFileName: I give up! Can't determine the quality so guess SD")

    if title: processedFilenameResults['title'] = title
    if season: processedFilenameResults['season'] = season
    if episode: processedFilenameResults['episode'] = episode
    if quality: processedFilenameResults['quality'] = quality
    if source: processedFilenameResults['source'] = source
    if releasegrp: processedFilenameResults['releasegrp'] = releasegrp
    log.debug("ProcessFileName: Returning %s" % processedFilenameResults)

    return processedFilenameResults


def matchQuality(quality, item):
    if quality == u"SD":
        if re.search('720', item):
            log.debug("matchQuality: Quality SD did not match to %s" % item)
            return None
        elif re.search('1080', item):
            log.debug("matchQuality: Quality SD did not match to %s" % item)
            return None
        else:
            log.debug("matchQuality: Quality matched SD to %s" % item)
            return 1
    elif quality == u"1080" and re.search('1080', item):
        log.debug("matchQuality: Quality is 1080 matched to %s" % item)
        return 1
    elif quality == u"720" and re.search('720', item):
        log.debug("matchQuality: Quality is 720 matched to %s" % item)
        return 1


def scoreMatch(release, quality, releasegrp, source):
    """
    Return how high the match is. Currently 7 is the best match
    This function give the flexibility to change the most important attribute for matching or even give the user the possibility to set his own preference
    release is the filename as it is in the result from bierdopje
    If quality is matched, score increased with 2
    If releasegrp is matched, score is increased with 1
    If source is matched, score is increased with 4
    """
    score = 0
    log.debug("scoreMatch: Giving a matchscore for: %s. Try to match it with Q: %s GRP: %s S: %s" % (release, quality, releasegrp, source))
    
    releasedict = ProcessFileName(release, None)
    releasesource = None
    releasequality = None
    releasereleasegrp = None
    
    if 'source' in releasedict.keys(): releasesource = releasedict['source']
    if 'quality' in releasedict.keys(): releasequality = releasedict['quality']
    if 'releasegrp' in releasedict.keys(): releasereleasegrp = releasedict['releasegrp']
    
    if releasegrp and releasereleasegrp:
        if releasereleasegrp == releasegrp:
            score += 1
    if source and releasesource:
        if releasesource == source:
            score += 4
    if quality and releasequality:
        if (matchQuality(quality, releasequality)):
            score += 2
    
    if not releasedict:
        log.warning("scoreMatch: Something went wrong, ProcessFileName could not process the file, %s, please report this!" %release)
        log.info("scoreMatch: Falling back to old matching system, to make sure you get your subtitle!")
        if releasegrp:
            if (re.search(re.escape(releasegrp), release, re.IGNORECASE)):
                score += 1
        if source:
            if (re.search(re.escape(source), release, re.IGNORECASE)):
                score += 4
        if quality:
            if (matchQuality(re.escape(quality), release)):
                score += 2
         
    log.debug("scoreMatch: MatchScore is %s" % str(score))
    return score


def nameMapping(showName):
    if showName.upper() in autosub.USERNAMEMAPPINGUPPER.keys():
        log.debug("nameMapping: found match in user's namemapping for %s" % showName)
        return autosub.USERNAMEMAPPINGUPPER[showName.upper()]
    elif showName.upper() in autosub.NAMEMAPPINGUPPER.keys():
        log.debug("nameMapping: found match for %s" % showName)
        return autosub.NAMEMAPPINGUPPER[showName.upper()]


def SkipShow(showName, season, episode):
    if showName.upper() in autosub.SKIPSHOWUPPER.keys():
        log.debug("SkipShow: Found %s in skipshow dictonary" % showName)
        for seasontmp in autosub.SKIPSHOWUPPER[showName.upper()]:
            if seasontmp == '0':
                log.debug("SkipShow: variable of %s is set to 0, skipping the complete Serie" % showName)
                return True
            elif int(seasontmp) == int(season):
                log.debug("SkipShow: Season matches variable of %s, skipping season" % showName)
                return True


def getShowid(show_name):
    log.debug('getShowid: trying to get showid for %s' %show_name)
    show_id = nameMapping(show_name)
    if show_id:
        log.debug('getShowid: showid from namemapping %s' %show_id)
        return int(show_id)
    
    show_id = idCache().getId(show_name)
    if show_id:
        log.debug('getShowid: showid from cache %s' %show_id)
        if show_id == -1:
            log.error('getShowid: showid not found for %s' %show_name)
            return
        return int(show_id)
    
    #do we have enough api calls?
    if checkAPICalls(use=False):
        show_id = autosub.Bierdopje.getShowidApi(show_name)
    else:
        log.warning("getShowid: Out of API calls")
        return None
    
    if show_id:
        log.debug('getShowid: showid from api %s' %show_id)
        idCache().setId(show_id, show_name)
        log.info('getShowid: %r added to cache with %s' %(show_name, show_id))
        return int(show_id)
    
    log.error('getShowid: showid not found for %s' %show_name)
    idCache().setId(-1, show_name)


def checkAPICalls(use=False):
    """
    Checks if there are still API calls left
    Set true if a API call is being made.
    """
    currentime = time.time()
    lastrun  = autosub.APICALLSLASTRESET
    interval = autosub.APICALLSRESETINT
    
    if currentime - lastrun > interval:
        autosub.APICALLS = autosub.APICALLSMAX
        autosub.APICALLSLASTRESET = time.time()
    
    if autosub.APICALLS > 0:
        if use==True:
            autosub.APICALLS-=1
        return True
    else:
        return False

