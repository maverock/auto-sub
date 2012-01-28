#This Script is an example of what is possible with the PostProcess feature of Auto-Sub
#The Current options available are:
# echo | simply echo the arguments given to the post process script
import sys
import libary.pythontwitter as twitter
import libary.oauth2 as oauth
try:
    from urlparse import parse_qsl 
except:
    from cgi import parse_qsl


#OPTIONS EDIT HERE

what = "echo"

#Twitter options:
token_key=''
token_secret=''
#/Twitter options

#/OPTIONS STOP EDITING BELOW THIS LINE
    
#TWITTER APPLICATION SOURCE
consumer_key='CRMvUogoJ5kMErtU9fiw'
consumer_secret='JqS5jJIWdokl5iijZmoBHNwRsknw7xmCxPggEsmo8'

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL        = 'https://api.twitter.com/oauth/authenticate'

def authorize_application():
    consumer = oauth.Consumer(key=consumer_key,secret=consumer_secret)
    oauth_client = oauth.Client(consumer)
    response, content = oauth_client.request(REQUEST_TOKEN_URL, 'GET')

    if response['status'] != '200':
        print "ERROR: Invalid response"
    else:
        request_token = dict(parse_qsl(content))
        print "Visit: " + AUTHORIZATION_URL + "?oauth_token=" + request_token['oauth_token']
    
    token_key = request_token['oauth_token']
    token_secret = request_token['oauth_token_secret']

    token = oauth.Token(token_key, token_secret)
    pin = raw_input('PIN: ').strip()
    token.set_verifier(pin)

    oauth_client2  = oauth.Client(consumer, token)
    response, content = oauth_client2.request(ACCESS_TOKEN_URL, method='POST', body='oauth_verifier=%s' % pin)
    access_token  = dict(parse_qsl(content))

    if response['status'] != '200':
        print "ERROR: Invalid response"
    else:
        token_key = access_token['oauth_token']
        token_secret = access_token['oauth_token_secret']
        print "token_key='%s'" %token_key
        print "token_secret='%s'" %token_secret 

def send_tweet(message):    
    try:
        api = twitter.Api(consumer_key, consumer_secret, token_key, token_secret)
        api.PostUpdate(message)
        print "Tweet sended!"
    except:
        print "ERROR: Could not send tweet, check token_key & token_secret"


#MAIN FUNCTION
if what == "echo":
    print
    print sys.argv[1]
    print sys.argv[2]

if what == "twitter":
    if token_key=="":
        authorize_application()  
    else:
        if (sys.argv[1] and sys.argv[2] and token_key!=""):
            var = sys.argv[1]
            var2 = sys.argv[2]
            
            var = var.split('/')
            var2 = var2.split('/')
            tweet = "Downloaded: " + var[-1] + " for " + var2[-1] 
            print "Sending the following tweet %s" %tweet
            send_tweet(tweet)
        elif (sys.argv[1] and sys.argv[2]):
            print "ERROR: token_key not set yet, run script without any arguments"