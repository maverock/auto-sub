import logging
import library.pynmwp as pynmwp
import autosub

log = logging.getLogger('thelogger')

def _send_notify(message):
    nmwp_instance  = pynmwp.PyNMWP(str(autosub.NMWPAPI))
    resp = nmwp_instance.push(application = "Auto-Sub", event = "Downloaded a Subtitle", description = message, priority = 0, batch_mode = False)
    try:
        if not resp[str(autosub.NMWPAPI)][u'Code'] == u'200':
            log.error("NMWP: Failed to send a notification")
            return False
        else:
            log.info("NMWP: Notification sent")
            return True
    except:
        log.error("NMWP: Something wrong with API-key, failed")

def test_notify():
    log.debug("NMWP: Trying to send a notification")
    message = "Auto-Sub successfully sent a test message"
    return _send_notify(message)
        
def send_notify(lang, subtitlefile, videofile):
    log.debug("NMWP: Trying to send a notification")
    message = "Auto-Sub just downloaded the following subtitle: \n %s" %subtitlefile
    return _send_notify(message)