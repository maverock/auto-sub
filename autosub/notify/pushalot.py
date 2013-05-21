import logging
import autosub
from xml.dom.minidom import parseString
from httplib import HTTPSConnection
from urllib import urlencode

log = logging.getLogger('thelogger')
pushalotapi = autosub.PUSHALOTAPI

def test_notify():
    return _send_notify(message="Testing Pushalot settings from AutoSub")

def send_notify(lang, subtitlefile, videofile):
    log.debug("Pushalot: Trying to send a notification")
    message = "Auto-Sub just downloaded the following subtitle: \n %s" %subtitlefile
    return _send_notify(message)

def _send_notify(message):

    if not autosub.NOTIFYPUSHALOT == True and not force:
            return False

    http_handler = HTTPSConnection("pushalot.com")

    data = {'AuthorizationToken': autosub.PUSHALOTAPI,
            'Title': "Auto-Sub",
            'Body': message.encode('utf-8') }

    try:
        http_handler.request("POST",
                                "/api/sendmessage",
                                headers = {'Content-type': "application/x-www-form-urlencoded"},
                                body = urlencode(data))
    except (SSLError, HTTPException):
        log.info("Pushalot notification failed.", log.error)
        return False
    response = http_handler.getresponse()
    request_status = response.status

    if request_status == 200:
            log.info("Pushalot: notification sent.")
            return True
    elif request_status == 410: 
            log.info("Pushalot auth failed: %s" % response.reason, log.error)
            return False
    else:
            log.info("Pushalot notification failed.", log.error)
            return False