import logging

import library.pynma as pynma

import autosub

log = logging.getLogger('thelogger')
        
def send_notify(lang, subtitlefile, videofile):
    log.debug("NMA: Try to send a notifications")
    message = "Auto-Sub just downloaded the following subtitle \n %s" %subtitlefile
    
    nma_instance = pynma.PyNMA(str(autosub.NMAAPI))
    resp = nma_instance.push('Auto-Sub', 'Downloaded a Subtitle', message)
    try:
        if not resp[str(autosub.NMAAPI)][u'code'] == u'200':
            log.error("NMA: Failed to send a notification")
            return False
        else:
            log.info("NMA: notification sended")
            return True
    except:
        log.error("NMA: Something wrong with API-key, failed")
    
def test_notify():
    log.debug("NMA: Try to send a notifications")
    message = "Auto-Sub sucessfully sended a test message"
    
    nma_instance = pynma.PyNMA(str(autosub.NMAAPI))
    resp = nma_instance.push('Auto-Sub', 'Testing', message)
    try:
        if not resp[str(autosub.NMAAPI)][u'code'] == u'200':
            log.error("NMA: Failed to send a notification")
            return False
        else:
            log.info("NMA: notification sended")
            return True
    except:
        log.error("NMA: Something wrong with API-key, failed")

        