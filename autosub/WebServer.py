import cherrypy

try:
    from Cheetah.Template import Template
except:
    print "ERROR!!! Cheetah is not installed yet. Download it from: http://pypi.python.org/pypi/Cheetah/2.4.4"

import threading
import time, os
import autosub.Config
from autosub.Db import idCache, lastDown

import autosub.notify as notify

# TODO: Create webdesign
class PageTemplate (Template):
    #Placeholder for future, this object can be used to add stuff to the template
    pass

class Config:
    @cherrypy.expose
    def index(self):
        tmpl = PageTemplate(file="interface/templates/config.tmpl")
        return str(tmpl)
    @cherrypy.expose
    def skipShow(self, title, season=None):
        if not season:
            tmpl = PageTemplate(file="interface/templates/config-skipshow.tmpl")
            tmpl.title = title
            return str(tmpl)
        else:
            tmpl = PageTemplate(file="interface/templates/message.tmpl")
            if not title:
                raise cherrypy.HTTPError(400, "No show supplied")
            if title.upper() in autosub.SKIPSHOWUPPER:
                for x in autosub.SKIPSHOWUPPER[title.upper()]:
                    if x == season or x == '0':
                        tmpl.message = "Already skipped <br> <a href='/home'>Return home</a>"
                        return str(tmpl)
                if season == '00':
                    season = season + ',' + ','.join(autosub.SKIPSHOWUPPER[title.upper()])
                else:
                    season = str(int(season)) + ',' + ','.join(autosub.SKIPSHOWUPPER[title.upper()])
            else:
                if not season == '00':
                    season = str(int(season))
            autosub.Config.SaveToConfig('skipshow',title,season)
            autosub.Config.applyskipShow()
            
            tmpl.message = "Add %s and season %s to the skipshow and applied it. <br> Remember, WantedQueue will be refresh at the next run of scanDisk <br> <a href='/home'>Return home</a>" % (title, season)
            return str(tmpl)
    
    @cherrypy.expose
    def applyConfig(self):
        autosub.Config.applyAllSettings()
        tmpl = PageTemplate(file="interface/templates/message.tmpl")
        tmpl.message = "Settings read & applied<br><a href='/config'>Return</a>"
        return str(tmpl)

    @cherrypy.expose
    def saveConfig(self, subeng, checksub, scandisk, minmatchscore, checkrss, subnl, minmatchscorerss, postprocesscmd, downloadsubs, path, logfile, rootpath, fallbacktoeng, downloadeng, username, password, skipshow, lognum, loglevelconsole, logsize, loglevel, webserverip, webserverport, usernamemapping, notifymail, notifygrowl, notifynma, notifytwitter, mailsrv, mailfromaddr, mailtoaddr, mailusername, mailpassword, mailsubject, mailencryption, growlhost, growlport, growlpass, nmaapi, twitterkey, twittersecret, notifyen, notifynl):
        # Set all internal variables
        autosub.PATH = path
        autosub.ROOTPATH = rootpath
        autosub.LOGFILE = logfile
        autosub.FALLBACKTOENG = fallbacktoeng
        autosub.DOWNLOADENG = downloadeng
        autosub.SUBENG = subeng
        autosub.SUBNL = subnl
        autosub.NOTIFYEN = notifyen
        autosub.NOTIFYNL = notifynl
        autosub.POSTPROCESSCMD = postprocesscmd
        autosub.MINMATCHSCORE = int(minmatchscore)
        autosub.MINMATCHSCORERSS = int(minmatchscorerss)
        autosub.SCHEDULERSCANDISK = int(scandisk)
        autosub.SCHEDULERCHECKSUB = int(checksub)
        autosub.SCHEDULERCHECKRSS = int(checkrss)
        autosub.SCHEDULERDOWNLOADSUBS = int(downloadsubs)
        autosub.LOGLEVEL = int(loglevel)
        autosub.LOGNUM = int(lognum)
        autosub.LOGSIZE = int(logsize)
        autosub.LOGLEVELCONSOLE = int(loglevelconsole)
        autosub.WEBSERVERIP = webserverip
        autosub.WEBSERVERPORT = int(webserverport)
        autosub.USERNAME = username
        autosub.PASSWORD = password
        autosub.SKIPSHOW = autosub.Config.stringToDict(skipshow)
        autosub.USERNAMEMAPPING = autosub.Config.stringToDict(usernamemapping)

        # Set all internal notify variables
        autosub.NOTIFYMAIL = notifymail
        autosub.MAILSRV = mailsrv
        autosub.MAILFROMADDR = mailfromaddr
        autosub.MAILTOADDR = mailtoaddr
        autosub.MAILUSERNAME = mailusername
        autosub.MAILPASSWORD = mailpassword
        autosub.MAILSUBJECT = mailsubject
        autosub.MAILENCRYPTION = mailencryption
        autosub.NOTIFYGROWL = notifygrowl
        autosub.GROWLHOST = growlhost
        autosub.GROWLPORT = growlport
        autosub.GROWLPASS = growlpass
        autosub.NOTIFYNMA = notifynma
        autosub.NMAAPI = nmaapi
        autosub.NOTIFYTWITTER = notifytwitter
        autosub.TWITTERKEY = twitterkey
        autosub.TWITTERSECRET = twittersecret

        # Now save to the configfile
        message = autosub.Config.WriteConfig()

        tmpl = PageTemplate(file="interface/templates/message.tmpl")
        tmpl.message = message
        return str(tmpl)

    @cherrypy.expose
    def flushCache(self):
        idCache().flushCache()
        message = 'Id Cache flushed'
        tmpl = PageTemplate(file="interface/templates/message.tmpl")
        tmpl.message = message
        return str(tmpl)
    
    @cherrypy.expose
    def flushLastdown(self):
        lastDown().flushLastdown()
        message = 'Last downloaded subtitle database flushed'
        tmpl = PageTemplate(file="interface/templates/message.tmpl")
        tmpl.message = message
        return str(tmpl)
    
    @cherrypy.expose
    def checkVersion(self):
        checkversion = autosub.Helpers.CheckVersion()
        
        if checkversion==True:
            message = 'There is a new version available! Visit: <a href=http://code.google.com/p/auto-sub/downloads/list>Google-Project</a>'
        elif checkversion == False:
            message = 'You are running the latest version!'
        elif checkversion == None:
            message = 'Something is wrong. Either we could not reach google-project. Or you are trying to compare different releases (Alpha with Beta).'
        
        tmpl = PageTemplate(file="interface/templates/message.tmpl")
        tmpl.message = message
        return str(tmpl)   
    
    @cherrypy.expose
    def testNotify(self, notifylib):
        if notify.notifyTest(notifylib):
            message = 'Sended a test message!'
        else:
            message = 'Failed to send a test message'
        tmpl = PageTemplate(file="interface/templates/message.tmpl")
        tmpl.message = message
        return str(tmpl) 
    
    @cherrypy.expose
    def regTwitter(self, token_key=None, token_secret=None, token_pin=None):
        import library.oauth2 as oauth
        import autosub.notify.twitter as notifytwitter 
        try:
            from urlparse import parse_qsl
        except:
            from cgi import parse_qsl
        
        if not token_key and not token_secret:
            consumer = oauth.Consumer(key=notifytwitter.CONSUMER_KEY, secret=notifytwitter.CONSUMER_SECRET)
            oauth_client = oauth.Client(consumer)
            response, content = oauth_client.request(notifytwitter.REQUEST_TOKEN_URL, 'GET')
            if response['status'] != '200':
                message = "Something went wrong..."
                tmpl = PageTemplate(file="interface/templates/message.tmpl")
                tmpl.message = message
                return str(tmpl)
            else:
                request_token = dict(parse_qsl(content))
                tmpl = PageTemplate(file="interface/templates/config-twitter.tmpl")
                tmpl.url = notifytwitter.AUTHORIZATION_URL + "?oauth_token=" + request_token['oauth_token']
                token_key = request_token['oauth_token']
                token_secret = request_token['oauth_token_secret']
                tmpl.token_key = token_key
                tmpl.token_secret = token_secret
                return str(tmpl)
        
        if token_key and token_secret and token_pin:
            
            token = oauth.Token(token_key, token_secret)
            token.set_verifier(token_pin)
            consumer = oauth.Consumer(key=notifytwitter.CONSUMER_KEY, secret=notifytwitter.CONSUMER_SECRET)
            oauth_client2 = oauth.Client(consumer, token)
            response, content = oauth_client2.request(notifytwitter.ACCESS_TOKEN_URL, method='POST', body='oauth_verifier=%s' % token_pin)
            access_token = dict(parse_qsl(content))

            if response['status'] != '200':
                message = "Something went wrong..."
                tmpl = PageTemplate(file="interface/templates/message.tmpl")
                tmpl.message = message
                return str(tmpl)
            else:
                autosub.TWITTERKEY = access_token['oauth_token']
                autosub.TWITTERSECRET = access_token['oauth_token_secret']
                
                message = "Twitter is now set up, remember to save your config and remember to test twitter! <br> <a href='/config'>Return</a>"
                tmpl = PageTemplate(file="interface/templates/message.tmpl")
                tmpl.message = message
                return str(tmpl)
                

class Home:
    @cherrypy.expose
    def index(self):
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        return str(tmpl)
    
    @cherrypy.expose
    def runNow(self):
        #time.sleep is here to prevent a timing issue, where checksub is runned before scandisk
        autosub.SCANDISK.runnow = True
        time.sleep(5)
        autosub.CHECKRSS.runnow = True
        autosub.CHECKSUB.runnow = True
        autosub.DOWNLOADSUBS.runnow = True
        
        tmpl = PageTemplate(file="interface/templates/message.tmpl")
        tmpl.message = "Running everything! <br> <a href='/home'>Return</a>"
        return str(tmpl)
    
    @cherrypy.expose
    def resetAPICalls(self):
        autosub.APICALLS = autosub.APICALLSMAX
        autosub.APICALLSLASTRESET = time.time()
        
        tmpl = PageTemplate(file="interface/templates/message.tmpl")
        tmpl.message = "API Calls reseted"
        return str(tmpl)
    
    @cherrypy.expose
    def shutdown(self):
        tmpl = PageTemplate(file="interface/templates/stopped.tmpl")
        threading.Timer(2, autosub.AutoSub.stop).start()
        return str(tmpl)

class Viewlog:
    @cherrypy.expose
    def index(self):
        tmpl = PageTemplate(file="interface/templates/viewlog.tmpl")
        maxLines = 500

        data = []
        if os.path.isfile(autosub.LOGFILE):
            f = open(autosub.LOGFILE)
            data = f.readlines()
            f.close()

        finalData = []

        numLines = 0

        numToShow = min(maxLines, len(data))

        for x in reversed(data):
            numLines += 1

            if numLines >= numToShow:
                break
            finalData.append(x)
        result = "".join(finalData)

        tmpl.message = result
        tmpl.logheader = 'All'
        return str(tmpl)

    @cherrypy.expose
    def info(self):
        tmpl = PageTemplate(file="interface/templates/viewlog.tmpl")
        maxLines = 500

        data = []
        if os.path.isfile(autosub.LOGFILE):
            f = open(autosub.LOGFILE)
            data = f.readlines()
            f.close()

        finalData = []

        numLines = 0

        numToShow = min(maxLines, len(data))

        for x in reversed(data):
            if x[24] == 'I':
                numLines += 1

                if numLines >= numToShow:
                    break
                finalData.append(x)
        result = "".join(finalData)

        tmpl.message = result
        tmpl.logheader = 'Info'
        return str(tmpl)

    @cherrypy.expose
    def debug(self):
        tmpl = PageTemplate(file="interface/templates/viewlog.tmpl")
        maxLines = 500

        data = []
        if os.path.isfile(autosub.LOGFILE):
            f = open(autosub.LOGFILE)
            data = f.readlines()
            f.close()

        finalData = []

        numLines = 0

        numToShow = min(maxLines, len(data))

        for x in reversed(data):
            if x[24] == 'D':
                numLines += 1

                if numLines >= numToShow:
                    break
                finalData.append(x)
        result = "".join(finalData)

        tmpl.message = result
        tmpl.logheader = 'Debug'
        return str(tmpl)

    @cherrypy.expose
    def error(self):
        tmpl = PageTemplate(file="interface/templates/viewlog.tmpl")
        maxLines = 500

        data = []
        if os.path.isfile(autosub.LOGFILE):
            f = open(autosub.LOGFILE)
            data = f.readlines()
            f.close()

        finalData = []

        numLines = 0

        numToShow = min(maxLines, len(data))

        for x in reversed(data):
            if x[24] == 'E':
                numLines += 1

                if numLines >= numToShow:
                    break
                finalData.append(x)
        result = "".join(finalData)

        tmpl.message = result
        tmpl.logheader = 'Error'
        return str(tmpl)

    @cherrypy.expose
    def warning(self):
        tmpl = PageTemplate(file="interface/templates/viewlog.tmpl")
        maxLines = 500

        data = []
        if os.path.isfile(autosub.LOGFILE):
            f = open(autosub.LOGFILE)
            data = f.readlines()
            f.close()

        finalData = []

        numLines = 0

        numToShow = min(maxLines, len(data))

        for x in reversed(data):
            if x[24] == 'W':
                numLines += 1

                if numLines >= numToShow:
                    break
                finalData.append(x)
        result = "".join(finalData)

        tmpl.message = result
        tmpl.logheader = 'Warning'
        return str(tmpl)

    @cherrypy.expose
    def critical(self):
        tmpl = PageTemplate(file="interface/templates/viewlog.tmpl")
        maxLines = 500

        data = []
        if os.path.isfile(autosub.LOGFILE):
            f = open(autosub.LOGFILE)
            data = f.readlines()
            f.close()

        finalData = []

        numLines = 0

        numToShow = min(maxLines, len(data))

        for x in reversed(data):
            if x[24] == 'C':
                numLines += 1

                if numLines >= numToShow:
                    break
                finalData.append(x)
        result = "".join(finalData)

        tmpl.message = result
        tmpl.logheader = 'Critical'
        return str(tmpl)


class WebServerInit():
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/home")
    
    home = Home()
    config = Config()
    viewlog = Viewlog()

    def error_page_401(status, message, traceback, version):
        return "Error %s - Well, I'm very sorry but you don't have access to this resource!" % status
    def error_page_404(status, message, traceback, version):
        return "Error %s - Well, I'm very sorry but this page could not be found!" % status
    def error_page_500(status, message, traceback, version):
        return "Error %s - Please refresh! If this error doesn't go away (after a few minutes), seek help!" % status
    _cp_config = {'error_page.401':error_page_401,
                  'error_page.404':error_page_404,
                  'error_page.500':error_page_500}
