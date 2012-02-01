import cherrypy
from Cheetah.Template import Template
import autosub
import threading

# TODO: Create webdesign
class PageTemplate (Template):
    #Placeholder for future, this object can be used to add stuff to the template
    #Like menu, footers etc. Currently this object does nothing
    pass

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
        raise cherrypy.HTTPRedirect("/home")
    
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