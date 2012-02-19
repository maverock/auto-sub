# Autosub autosub/wipStatus.py - http://code.google.com/p/auto-sub/
#
# The Autosub checkStatus module
#


import urllib2
import re
import autosub
from library.beautifulsoup import BeautifulSoup

import socket
socket.setdefaulttimeout(autosub.TIMEOUT)

class wipStatus():
    def run(self):
        try:
            response = urllib2.urlopen(autosub.WIPURL)   
        except:
            return False
        simpleregex = re.compile("^((?P<title>.+?)[. _-]+)?s(?P<season>\d+)[x. _-]*e(?P<episode>\d+)",re.IGNORECASE)
        test = re.compile('progressBar')
        title = re.compile('verwacht')
        
        getdate = re.compile('(\d+/\d+/\d+)')
        getprocent = re.compile('\d+%')
        
        soup = BeautifulSoup(response.read())
        
        dates = {}
        proc = {}
        
        x = soup.findAll('span', {'class' : 'lijstitem'})
        
        for x in soup.findAll('span', {'class' : 'lijstitem'}):
            yy = x.findAll('span', {'class': test,'title':title})
            for y in x.findAll('a', {'class' : 'icon_link'}):
                for z in y.findAll(text=True):
                    try:
                        match = re.search(getdate,str(yy[0]))
                        match2 = re.search(getprocent,str(yy[0]))
                        dates[str(z)] = match.group(0)
                        proc[str(z)] = match2.group(0)
                        break
                    except:
                        break
        
        for y in dates.keys():
            matches = simpleregex.search(y)
            try:
                matchdic = matches.groupdict()
            except:
                continue
            title = matchdic['title']
            season = matchdic['season']
            episode = matchdic['episode']
            for x in autosub.WANTEDQUEUE:
                if x['title'] == title and x['season'] == season and x['episode'] == episode:
                    x['WIPDate'] = dates[y]
         
        for y in proc.keys():
            matches = simpleregex.search(y)
            try:
                matchdic = matches.groupdict()
            except:
                continue
            title = matchdic['title']
            season = matchdic['season']
            episode = matchdic['episode']
            for x in autosub.WANTEDQUEUE:
                if x['title'] == title and x['season'] == season and x['episode'] == episode:
                    x['WIPProc'] = proc[y]                                 
            
        return True
