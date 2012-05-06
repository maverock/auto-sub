# Autosub notify library - http://code.google.com/p/auto-sub/
# Every function should have 2 calls, send_notify and test_notify
# Send notify should get 3 argument: videofile, subtitlefile (both without path) and lang (which should be the language)
# test_notify doesn't require any argument
# every module should return True if success, and False when failed

import logging
import os

import autosub

from autosub.notify import twitter
from autosub.notify import mail

log = logging.getLogger('thelogger')

def notifyTest(notifylib):
    """
    Simple function to send a test message. 
    Notifylib should be a string containing which library is required
    """
    if notifylib == 'twitter':
        log.info("Notify: Sending test tweet")
        return twitter.test_notify()
    
    if notifylib == 'mail':
        log.info("Notify: Sending test mail")
        return mail.test_notify()

def notify(lang, subtitlefile, videofile):
    log.debug("Notify: Trying to send notifications. Language: %s Srt: %s Video: %s" %(lang, subtitlefile, videofile))
    #Lets strip video file and subtitle file of its path!
    subtitlefile = os.path.basename(subtitlefile)
    videofile = os.path.basename(videofile)
    
    if lang == 'en' and autosub.NOTIFYEN:
        notifySend(lang, subtitlefile, videofile)
    if lang == 'nl' and autosub.NOTIFYNL:
        notifySend(lang, subtitlefile, videofile)

def notifySend(lang, subtitlefile, videofile):
    if autosub.NOTIFYTWITTER:
        log.debug("Notify: Twitter is enabled")
        twitter.send_notify(lang, subtitlefile, videofile)
    
    if autosub.NOTIFYMAIL:
        log.debug("Notify: Mail is enabled")
        mail.send_notify(lang, subtitlefile, videofile)

