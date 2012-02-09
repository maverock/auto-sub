import cherrypy
from Cheetah.Template import Template
import threading
import autosub.Config

# TODO: Create webdesign
class PageTemplate (Template):
    #Placeholder for future, this object can be used to add stuff to the template
    #Like menu, footers etc. Currently this object does nothing
    pass

class Config:
    @cherrypy.expose
    def index(self):
        tmpl = PageTemplate(file="interface/templates/config.tmpl")
        return str(tmpl)
    @cherrypy.expose
    def skipShow(self, title, season):
        if not title:
            raise cherrypy.HTTPError(400, "No show supplied")
        if title.upper() in autosub.SKIPSHOWUPPER:
            for x in autosub.SKIPSHOWUPPER[title.upper()]:
                if x == season or x == '0':
                    return "Already skipped <br> <a href='/home'>Return home</a>"
            season = str(int(season)) + ',' +','.join(autosub.SKIPSHOWUPPER[title.upper()])
        else:
            season = str(int(season))
        autosub.Config.SaveToConfig('skipshow',title,season)
        autosub.Config.applyskipShow()
        return "Add %s and season %s to the skipshow and applied it. <br> Remember, WantedQueue will be refresh at the next run of scanDisk <br> <a href='/home'>Return home</a>" % (title, season)
    
    @cherrypy.expose
    def applyConfig(self):
        autosub.Config.applyAllSettings()
        return "Settings read & applied<br><a href='/config'>Return</a>"
class Home:
    @cherrypy.expose
    def index(self):
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        return str(tmpl)
    
    @cherrypy.expose
    def runNow(self):
        autosub.SCANDISK.runnow = True
        autosub.CHECKRSS.runnow = True
        autosub.CHECKSUB.runnow = True
        autosub.DOWNLOADSUBS.runnow = True
        autosub.WIPSTATUS.runnow = True
        return "Running everything! <br> <a href='/home'>Return</a>"
    
    @cherrypy.expose
    def runwipStatusNow(self):
        autosub.WIPSTATUS.runnow = True
        return "WipStatus updating <br> <a href='/home'>Return</a>"
    
    @cherrypy.expose
    def shutdown(self):
        tmpl = PageTemplate(file="interface/templates/stopped.tmpl")
        threading.Timer(2, autosub.AutoSub.stop).start()
        return str(tmpl)
    
class WebServerInit():

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/home")
    
    home = Home()
    config = Config()

    def error_page_401(status, message, traceback, version):
        return "Error %s - Well, I'm very sorry but you don't have access to this resource!" % status
    def error_page_404(status, message, traceback, version):
        return "Error %s - Well, I'm very sorry but this page could not be found!" % status
    _cp_config = {'error_page.401':error_page_401,
                  'error_page.404':error_page_404}
